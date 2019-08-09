import os
from faker import Faker
import time
import socket
from cloudflareddns import cloudflareddns
import platform

# change dir to tests directory to make relative paths possible
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def test_update():

    cf_username = os.environ['CF_EMAIL']
    cf_key = os.environ['CF_KEY']
    # hostname should be Python version specific so that different versions tests
    # don't jump onto each other, so test271.example.com, test368.example.com, etc.
    hostname = 'python{}.cloudflareddns.test.{}'.format(
        platform.python_version(),
        os.environ['CLOUDFLAREDDNS_TEST_DOMAIN'])

    faker = Faker()
    ip = faker.ipv4()

    print("Updating to random IP: {}".format(ip))

    # cf_username, cf_key, hostname, ip, proxied=False
    cloudflareddns.update(cf_username, cf_key, hostname, ip, False)

    time.sleep(180)

    # fetch record
    new_ip = socket.gethostbyname(hostname)
    print("Resolved IP after update is: {}".format(new_ip))

    assert new_ip == ip
