#!/usr/bin/env python

import os
import sys
import re
import json
import requests
import argparse
import tldextract
import CloudFlare
import logging as log  # for verbose output
import socket  # to get default hostname
from .__about__ import __version__


def update(cf_username, cf_key, hostname, ip, proxied=True, ttl=120):

    log.info("Updating {} to {}".format(hostname, ip))

    # get zone name correctly (from hostname)
    zone_domain = tldextract.extract(hostname).registered_domain
    log.info("Zone domain of hostname is {}".format(zone_domain))

    if ':' in ip:
        ip_address_type = 'AAAA'
    else:
        ip_address_type = 'A'

    cf = CloudFlare.CloudFlare(email=cf_username, token=cf_key)
    # now get the zone id
    try:
        params = {'name': zone_domain}
        zones = cf.zones.get(params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        log.error('badauth - %s' % (e))
        exit()
    except Exception as e:
        exit('/zones.get - %s - api call failed' % (e))

    if len(zones) == 0:
        log.error('nohost')
        exit()

    if len(zones) != 1:
        exit('/zones.get - %s - api call returned %d items' % (zone_domain, len(zones)))

    zone_id = zones[0]['id']
    log.info("Zone ID is {}".format(zone_id))

    try:
        params = {'name': hostname, 'match': 'all', 'type': ip_address_type}
        dns_records = cf.zones.dns_records.get(zone_id, params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones/dns_records %s - %d %s - api call failed' % (hostname, e, e))

    updated = False

    # update the record - unless it's already correct
    for dns_record in dns_records:
        old_ip = dns_record['content']
        old_ip_type = dns_record['type']

        if ip_address_type not in ['A', 'AAAA']:
            # we only deal with A / AAAA records
            continue

        if ip_address_type != old_ip_type:
            # only update the correct address type (A or AAAA)
            # we don't see this becuase of the search params above
            log.info('IGNORED: %s %s ; wrong address family' % (hostname, old_ip))
            continue

        if ip == old_ip:
            log.info('UNCHANGED: %s %s' % (hostname, ip))
            updated = True
            continue

        # Yes, we need to update this record - we know it's the same address type

        dns_record_id = dns_record['id']
        dns_record = {
            'name': hostname,
            'type': ip_address_type,
            'content': ip,
            'proxied': proxied,
            'ttl': ttl
        }
        try:
            dns_record = cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/zones.dns_records.put %s - %d %s - api call failed' % (hostname, e, e))
        log.info('UPDATED: %s %s -> %s' % (hostname, old_ip, ip))
        updated = True

    if not updated:
        # no exsiting dns record to update - so create dns record
        dns_record = {
            'name': hostname,
            'type': ip_address_type,
            'content': ip,
            'ttl': ttl
        }
        try:
            dns_record = cf.zones.dns_records.post(zone_id, data=dns_record)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/zones.dns_records.post %s - %d %s - api call failed' % (hostname, e, e))
        log.info('CREATED: %s %s' % (hostname, ip))

    # reached far enough, all good then (the text is required by Synology)
    print('good')


def main():
    parser = argparse.ArgumentParser(description='Update DDNS in Cloudflare.')
    parser.add_argument('--email', help='Cloudflare account emai')
    parser.add_argument('--key', help='Cloudflare API key')
    parser.add_argument('--hostname', metavar='HOSTNAME',
                        help='Hostname to set IP for')
    parser.add_argument('--ip', dest='ip',
                        help='The IP address')
    parser.add_argument('--verbose', dest='verbose', action='store_true')

    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))

    parser.set_defaults(hostname=socket.getfqdn())

    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    cf_username = args.email
    cf_key = args.key
    hostname = args.hostname
    ip = args.ip

    update(cf_username, cf_key, hostname, ip)


def syno():
    update(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


if __name__ == '__main__':
    main()
