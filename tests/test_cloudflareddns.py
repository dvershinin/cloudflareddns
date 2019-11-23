import os
from faker import Faker
import time
import socket
from cloudflareddns import cloudflareddns
import platform

# change dir to tests directory to make relative paths possible
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def test_update():

    cfUsername = os.environ['CF_EMAIL']
    cfKey = os.environ['CF_KEY']
    # hostname should be Python version specific so that different versions tests
    # don't jump onto each other, so test271.example.com, test368.example.com, etc.
    # this test waits for actual DNS update so we suffix it with "m" in case
    # in order for other tests (if they run earlier) not to update the same
    hostname = 'python{}m.cloudflareddns.test.{}'.format(
        platform.python_version(),
        os.environ['CLOUDFLAREDDNS_TEST_DOMAIN'])

    faker = Faker()
    ip = faker.ipv4()

    print("Updating to random IP: {}".format(ip))

    # cfUsername, cfKey, hostname, ip, ttl=None
    cloudflareddns.update(cfUsername, cfKey, hostname, ip, 120)

    time.sleep(180)

    # fetch record
    newIp = socket.gethostbyname(hostname)
    print("Resolved IP after update is: {}".format(newIp))

    assert newIp == ip


def test_update_success_status():

    cfUsername = os.environ['CF_EMAIL']
    cfKey = os.environ['CF_KEY']
    # hostname should be Python version specific so that different versions tests
    # don't jump onto each other, so test271.example.com, test368.example.com, etc.
    hostname = 'python{}.cloudflareddns.test.{}'.format(
        platform.python_version(),
        os.environ['CLOUDFLAREDDNS_TEST_DOMAIN'])

    faker = Faker()
    ip = faker.ipv4()

    print("Updating to random IP: {}".format(ip))

    res = cloudflareddns.update(cfUsername, cfKey, hostname, ip, 120)

    # fetch record
    assert res in ['good', 'nochg']


def test_update_record_func_success():

    hostname = 'python{}.cloudflareddns.test.{}'.format(
        platform.python_version(),
        os.environ['CLOUDFLAREDDNS_TEST_DOMAIN'])

    faker = Faker()
    ip = faker.ipv4()

    res = cloudflareddns.updateRecord(hostname, ip)

    assert res is True


def test_update_record_func_failure():

    # something we surely don't own and can't update:
    hostname = 'foo.example.com'.format(
        platform.python_version(),
        os.environ['CLOUDFLAREDDNS_TEST_DOMAIN'])

    faker = Faker()
    ip = faker.ipv4()

    res = cloudflareddns.updateRecord(hostname, ip)

    assert res is False
