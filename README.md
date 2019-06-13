# lastversion 

[![Build Status](https://travis-ci.org/dvershinin/cloudflareddns.svg?branch=master)](https://travis-ci.org/dvershinin/cloudflareddns)
[![PyPI version](https://badge.fury.io/py/cloudflareddns.svg)](https://badge.fury.io/py/cloudflareddns)

A tiny command line utility for implementing DDNS with Cloudflare.

* Supports virtually any server that is capable of running Python
* Synology DiskStations supported
* Quick to install using `pip`

## Synopsys


### Linux servers

```
usage: cloudflareddns [-h] [--email EMAIL] [--key KEY] [--hostname HOSTNAME]
                      [--ip IP] [--verbose] [--version]

Update DDNS in Cloudflare.

optional arguments:
  -h, --help           show this help message and exit
  --email EMAIL        Cloudflare account emai
  --key KEY            Cloudflare API key
  --hostname HOSTNAME  Hostname to set IP for
  --ip IP              The IP address
  --verbose
  --version            show program's version number and exit
```

### Synology DiskStations

You can configure a Synology DiskStation with CloudFlare DDNS.
    
#### Step 1. Access Synology via SSH

* Login to your DSM
* Go to Control Panel > Terminal & SNMP > Enable SSH service
* Use your client or commandline to access Synology. If you don't have any, I recommand you can try out MobaXterm for Windows.
* Use your Synology admin account to connect.
* Run the following command to add new DDNS provider:

```
cat >> /etc/ddns_provider.conf << 'EOF'
[USER_Cloudflare]
        modulepath=/usr/local/CloudflareDDNS/bin/cloudflareddns-syno
        queryurl=https://www.cloudflare.com/
EOF
```

#### Step 2. Install `cloudflareddns`

Sure enough you can just `pip install cloudflareddns`. But the safest approach to your system is using `virtualenv` :)

```
curl https://bootstrap.pypa.io/get-pip.py | python
pip install virtualenv
# create virtualenv twice to ensure creation of "activate" script
virtualenv /usr/local/CloudflareDDNS
virtualenv /usr/local/CloudflareDDNS
# go inside our virtualenv
. /usr/local/CloudflareDDNS/bin/activate
# install the packages we need there (cloudflare will be used in the future):
pip install cloudflareddns
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
    
## Installation for other systems

Installing with `pip` is easiest:

    pip install cloudflareddns

