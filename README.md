# cloudflareddns 

[![Build Status](https://travis-ci.org/dvershinin/cloudflareddns.svg?branch=master)](https://travis-ci.org/dvershinin/cloudflareddns)
[![PyPI version](https://badge.fury.io/py/cloudflareddns.svg)](https://badge.fury.io/py/cloudflareddns)

A tiny command line utility for implementing DDNS with Cloudflare.

* Supports virtually any server that is capable of running Python
* Synology DiskStations supported
* Quick to install using `pip`

## Synopsys

```
usage: cloudflareddns [-h] [--email EMAIL] [--key KEY] [--hostname HOSTNAME]
                      [--ip IP] [--ttl TTL] [--verbose] [--version]

Update DDNS in Cloudflare.

optional arguments:
  -h, --help           show this help message and exit
  --email EMAIL        Cloudflare account email (omit if using API tokens)
  --key KEY            Cloudflare API key or token
  --hostname HOSTNAME  Hostname to set IP for
  --ip IP              The IP address
  --ttl TTL            TTL in seconds
  --verbose
  --version            show program's version number and exit
```

When invoked without any options, `cloudflareddns` will try to point
FQDN of the machine it runs on to its public IP address (auto-detected).

### Install and use with Synology DiskStations

You can configure a Synology DiskStation with CloudFlare DDNS.

**It's worth noting that if your Synology DSM is recent enough, you can simply use Synology's own DDNS service, then create a `CNAME` record at your domain that points to it. The downside to this solution, however, is extra DNS lookup required to resolve domain to IP.**

Alternative solution is to use `cloudflaredns` which ships with the necessary CLI interface for Synology compatibility: `cloudflareddns-syno`.
    
#### Step 1. Access Synology via SSH

* Login to your DSM
* Go to Control Panel > Terminal & SNMP > Enable SSH service
* Use your client or commandline to access Synology. If you don't have any, I recommend you try out Putty for Windows.
* Use your Synology admin account to connect.

#### Step 2. Install `cloudflareddns`

If you're not a lazy man, checkout [instructions on installing using virtualenv](SAFE-INSTALL.md) for this step.
For quick setup instead:

    curl https://bootstrap.pypa.io/get-pip.py | python
    pip install cloudflareddns

Run the following command to add new DDNS provider:

```
cat >> /etc/ddns_provider.conf << 'EOF'
[USER_Cloudflare]
        modulepath=/bin/cloudflareddns-syno
        queryurl=https://www.cloudflare.com/
EOF
```

#### Step 3. Get Cloudflare parameters

The most secure solution is using an API *token* only.
(The old way of API email+*key* pair is still supported).

To generate a *token*, go to your [Cloudflare dashboard](https://dash.cloudflare.com/profile/api-tokens),
then click on "Create Token". Using the following "Permissions":

* Zone
* DNS
* Edit

And select your specific domain in "Zone Resources":

* Include
* Specific zone
* example.com (adjust to your domain, of course)


Now you've got the token. 

#### Step 4. Setup DDNS

* Login to your DSM
* Go to Control Panel > External Access > DDNS > Add
* Select Cloudflare as service provider
* Enter your domain as hostname, `x` in the Username/Email, and API token as Password/Key
    
The requirement to put `x` is due to Synology GUI's constraints not allowing for an empty field.    

### Installation for CentOS 7

    yum install https://extras.getpagespeed.com/release-el7-latest.rpm
    yum install python2-cloudflareddns
    
### Installation for other systems

Installing with `pip` is easiest:

    pip install cloudflareddns

### Usage in Python scripts

```python
from cloudflareddns import cloudflareddns
hostname = 'foo.example.com'
ip = '1.2.3.4'
if cloudflareddns.updateRecord(hostname, ip):
  print('Record is OK')
  ...
```

Requires using environment variables (see tips below).

## Cloudflare credentials


### Storing credentials

In non-Synology system, you can store Cloudflare credentials in either environment 
variables or a configuration file.

#### Configuration file

Create `~/.cloudflare/cloudflare.cfg` and put:

```ini
[CloudFlare]
email = user@example.com # Do not set if using an API Token
token = xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### Environment variables

You can put your Cloudflare credentials into the `~/.bashrc` file:

```bash
export CF_API_EMAIL="user@example.com" # Do not set if using an API Token
export CF_API_KEY="xxxxxx"
```

Don't forget to `source ~/.bashrc` if you have just put credentials in there.
The `cloudflareddns` will pick those up, so no need to pass `--email` or `--key` every time.