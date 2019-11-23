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
  --email EMAIL        Cloudflare account emai
  --key KEY            Cloudflare API key
  --hostname HOSTNAME  Hostname to set IP for
  --ip IP              The IP address
  --ttl TTL
  --verbose
  --version            show program's version number and exit
```

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

Go to your account setting page and get API Key.

#### Step 4. Setup DDNS

* Login to your DSM
* Go to Control Panel > External Access > DDNS > Add
* Select Cloudflare as service provider. Enter your domain as hostname, your Cloudflare account as Username/Email, and API key as Password/Key
    

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

### Tips

In non-Synology system, it's best to place your Cloudflare credentials into `~/.bashrc` as opposed
to passing them on the command-line. A `.bashrc` may have:

```bash
export CF_EMAIL="john@example.com"
export CF_KEY="xxxxxx"
```

Don't forget to `source ~/.bashrc` if you have just put credentials in there.
The `cloudflareddns` will pick those up, so no need to pass `--email` or `--key` every time.