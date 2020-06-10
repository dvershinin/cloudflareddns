"""
cloudflareddns
==========
License: BSD, see LICENSE for more details.
"""

import argparse
import logging as log  # for verbose output
import os
import socket  # to get default hostname
import sys

import CloudFlare
import requests
import tldextract
from CloudFlare.exceptions import CloudFlareAPIError

from .__about__ import __version__


def get_public_ip():
    log.debug('Getting public IP from an external service')
    return requests.get('https://ident.me').text


def cloudflare_creds_helper(email=None, key=None):
    """
    Ensures a few things:
    * priority of explicitly passed (e.g. on cmd-line) creds over env ones
    * puts creds to in env for read by Cloudflare pkg code (security
    * convert old naming of vars, to ones supported by Cloudflare pkg
    * e.g. CF_EMAIL (our old) => CF_API_EMAIL (Cloudflare pkg)
    :param email:
    :param key:
    """
    # allow special value 'x' for email when using TOKENs
    # in Synology GUI (which requires something for user/email field)
    if email == 'x':
        email = None

    # clear out env vars, so that we can be explicit with the TOKEN that we use in command line
    # can't clear out config file though, but meh.
    if key and not email:
        if 'CF_API_EMAIL' in os.environ:
            del os.environ['CF_API_EMAIL']
        if 'CF_API_KEY' in os.environ:
            del os.environ['CF_API_KEY']

    # support old naming of env vars
    if 'CF_EMAIL' in os.environ and 'CF_API_EMAIL' not in os.environ:
        os.environ['CF_API_EMAIL'] = os.getenv('CF_EMAIL')
    if 'CF_KEY' in os.environ and 'CF_API_KEY' not in os.environ:
        os.environ['CF_API_KEY'] = os.getenv('CF_KEY')

    if 'CF_API_TOKEN' in os.environ:
        os.environ['CF_API_KEY'] = os.getenv('CF_API_TOKEN')
        if 'CF_API_EMAIL' in os.environ:
            del os.environ['CF_API_EMAIL']

    if email:
        # allow special value 'x' for email when using TOKENs
        # in Synology GUI (which requires something user/email field)
        if email == 'x':
            email = None
        os.environ['CF_API_EMAIL'] = email

    if key:
        # clear out env vars, so that we can be explicit with the TOKEN that we use in command line
        # can't clear out config file though, but meh.
        if not email and 'CF_API_EMAIL' in os.environ:
            del os.environ['CF_API_EMAIL']
        os.environ['CF_API_KEY'] = key


def update(hostname, ip, ttl=None):
    """
    Create or update desired DNS record.
    Returns Synology-friendly status strings:
    https://community.synology.com/enu/forum/17/post/57640?reply=213305
    """
    log.debug("Updating {} to {}".format(hostname, ip))

    # get zone name correctly (from hostname)
    zoneDomain = tldextract.extract(hostname).registered_domain
    log.debug("Zone domain of hostname is {}".format(zoneDomain))

    if not zoneDomain:
        return 'nohost'

    if ':' in ip:
        ipAddressType = 'AAAA'
    else:
        ipAddressType = 'A'

    cf = CloudFlare.CloudFlare()
    # now get the zone id
    try:
        params = {'name': zoneDomain}
        zones = cf.zones.get(params=params)
    except CloudFlareAPIError as e:
        log.error('Bad auth - %s' % e)
        return 'badauth'
    except Exception as e:
        log.error('/zones.get - %s - api call failed' % e)
        return '911'

    if len(zones) == 0:
        log.error('No host')
        return 'nohost'

    if len(zones) != 1:
        log.error('/zones.get - %s - api call returned %d items' % (zoneDomain, len(zones)))
        return 'notfqdn'

    zone_id = zones[0]['id']
    log.debug("Zone ID is {}".format(zone_id))

    try:
        params = {'name': hostname, 'match': 'all', 'type': ipAddressType}
        dns_records = cf.zones.dns_records.get(zone_id, params=params)
    except CloudFlareAPIError as e:
        log.error('/zones/dns_records %s - %d %s - api call failed' % (hostname, e, e))
        return '911'

    desiredRecordData = {
        'name': hostname,
        'type': ipAddressType,
        'content': ip
    }
    if ttl:
        desiredRecordData['ttl'] = ttl

    # update the record - unless it's already correct
    for dnsRecord in dns_records:
        oldIp = dnsRecord['content']
        oldIpType = dnsRecord['type']

        if ipAddressType not in ['A', 'AAAA']:
            # we only deal with A / AAAA records
            continue

        if ipAddressType != oldIpType:
            # only update the correct address type (A or AAAA)
            # we don't see this becuase of the search params above
            log.debug('IGNORED: %s %s ; wrong address family' % (hostname, oldIp))
            continue

        if ip == oldIp:
            log.info('UNCHANGED: %s == %s' % (hostname, ip))
            # nothing to do, record already matches to desired IP
            return 'nochg'

        # Yes, we need to update this record - we know it's the same address type
        dnsRecordId = dnsRecord['id']

        try:
            cf.zones.dns_records.put(zone_id, dnsRecordId, data=desiredRecordData)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            log.error('/zones.dns_records.put %s - %d %s - api call failed' % (hostname, e, e))
            return '911'
        log.info('UPDATED: %s %s -> %s' % (hostname, oldIp, ip))
        return 'good'

    # no exsiting dns record to update - so create dns record
    try:
        cf.zones.dns_records.post(zone_id, data=desiredRecordData)
        log.info('CREATED: %s %s' % (hostname, ip))
        return 'good'
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        log.error('/zones.dns_records.post %s - %d %s - api call failed' % (hostname, e, e))
        return '911'

    # reached far enough without genuine return/exception catching, must be an error
    # using 'badagent' just because it is unique to other statuses used above
    return 'badagent'


def updateRecord(hostname, ip, ttl=None):
    res = update(hostname, ip, ttl)
    return res in ['good', 'nochg']


def main():
    parser = argparse.ArgumentParser(description='Update DDNS in Cloudflare.')
    parser.add_argument('--email', help='Cloudflare account email (omit if using API tokens)')
    parser.add_argument('--key', help='Cloudflare API key or token')
    parser.add_argument('--hostname', metavar='HOSTNAME',
                        help='Hostname to set IP for')
    parser.add_argument('--ip', dest='ip',
                        help='The IP address')
    parser.add_argument('--ttl', type=int, help='TTL in seconds')
    parser.add_argument('--verbose', dest='verbose', action='store_true')

    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))

    # we now use same env variables as Cloudflare Python package, but supporting older ones
    # e.g. CF_EMAIL (our old) => CF_API_EMAIL (Cloudflare package naming)
    if 'CF_EMAIL' in os.environ and 'CF_API_EMAIL' not in os.environ:
        os.environ['CF_API_EMAIL'] = os.getenv('CF_EMAIL')
    if 'CF_KEY' in os.environ and 'CF_API_KEY' not in os.environ:
        os.environ['CF_API_KEY'] = os.getenv('CF_KEY')

    parser.set_defaults(hostname=socket.getfqdn(), ttl=None, email=None, key=None)

    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.debug("Verbose output.")
    else:
        log.basicConfig(format="%(message)s", level=log.INFO)

    if not args.ip:
        args.ip = get_public_ip()

    cloudflare_creds_helper(args.email, args.key)

    update(args.hostname, args.ip, args.ttl)


def syno():
    """
    In Synology wrapper, we echo the return value (e.g. "nochg") of the "update"
    method for users to see status
    """

    parser = argparse.ArgumentParser(description='Update DDNS in Cloudflare, for Synology.')
    # Synology passes arguments in this order: username, password, hostname, ip
    parser.add_argument('email', help='Cloudflare account E-Mail. '
                                      'Specify "x" instead, if using an API token')
    parser.add_argument('key', help='Cloudflare API key or token')
    parser.add_argument('hostname', help='Hostname to set IP for')
    parser.add_argument('ip', help='The IP address')

    parser.add_argument('--verbose', dest='verbose', action='store_true')

    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))

    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.debug("Verbose output.")
    else:
        log.basicConfig(format="%(message)s", level=log.INFO)

    # set passed parameters to environment, for Cloudflare module to see
    cloudflare_creds_helper(args.email, args.key)

    print(
        update(
            hostname=args.hostname,
            ip=args.ip,
            ttl=120
        )
    )


if __name__ == '__main__':
    main()
