## Virtualenv Install

Sure enough you can just `pip install cloudflareddns`. But the safest approach to your system is using `virtualenv`.
For example, in Synology systems this will go down to:

```
curl https://bootstrap.pypa.io/get-pip.py | python
pip install virtualenv
# create virtualenv twice to ensure creation of "activate" script
virtualenv /usr/local/CloudflareDDNS
virtualenv /usr/local/CloudflareDDNS
# go inside our virtualenv
. /usr/local/CloudflareDDNS/bin/activate
pip install cloudflareddns
```

Run the following command to add new DDNS provider:

```
cat >> /etc/ddns_provider.conf << 'EOF'
[USER_Cloudflare]
        modulepath=/usr/local/CloudflareDDNS/bin/cloudflareddns-syno
        queryurl=https://www.cloudflare.com/
EOF
```