import random
import tarfile
import os

import logging
from random import Random

import contextlib
import time
import stat
import pwd
import webob
import eventlet
import uuid

from nae.common import cfg
from nae.common import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


class ResponseSucceed(object):
    def __call__(self):
        result = webob.Response(status=200)

        return result


def execute(func, *args):
    eventlet.spawn_n(func, *args)


def random_port():
    port_range = [4000, 65535]
    random_port = random.randint(int(port_range[0]), int(port_range[1]))

    return random_port


def random_str(randomlength=8):
    str = ''
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def get_file_path(user_name, repo_name):
    base_dir = os.path.expandvars('$HOME')
    user_dir = os.path.join(base_dir, user_name, repo_name)

    return user_dir


def repo_exist(user_name, repo_name):
    user_dir = os.path.join(os.path.expandvars('$HOME'), user_name)
    repo_dir = os.path.join(user_dir, repo_name)
    if not os.path.exists(repo_dir):
        return False
    return True


def human_readable_size(size):
    import humanize

    return humanize.naturalsize(size)


def human_readable_time(timestamp):
    _localtime = time.localtime(timestamp)
    _time_format = "%Y-%m-%d %H:%M:%S"

    return time.strftime(_time_format, _localtime)


def create_user_access(user_name):
    user_home = make_user_home(user_name)
    os.system('useradd -d {} -s /bin/bash {}'.format(user_home, user_name))
    os.system('echo {} | passwd {} --stdin'.format(random_str(), user_name))


@contextlib.contextmanager
def cd_change(tmp_location):
    cd = os.getcwd()
    os.chdir(tmp_location)
    try:
        yield
    finally:
        os.chdir(cd)


def make_zip_tar(path):
    docker_file = os.path.join(path, 'Dockerfile')
    if not os.path.isfile(docker_file):
        path = generate_docker_file()
    _str = random_str()
    tar = tarfile.open("/tmp/%s.tar.gz" % _str, "w:gz")
    with cd_change(path):
        for file in os.listdir(path):
            if file[0] == '.':
                continue
            tar.add(file)
    tar.close()

    return "/tmp/%s.tar.gz" % _str


def generate_docker_file():
    _str = random_str()
    temp_path = "/tmp/%s" % _str
    os.mkdir(temp_path)
    LOG.info("temp_path:%s" % temp_path)
    with open(os.path.join(temp_path, "Dockerfile"), 'w') as docker_file:
        docker_file.write("FROM centos:6.4\n")
        docker_file.write("EXPOSE 80 22\n")
    return temp_path


def create_root_path(user_id, uuid):
    """Create container root directory for each container and
       each user."""
    path = os.path.expandvars('$HOME')
    root_path = os.path.join(path, user_id, uuid, "www")
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    return root_path


def create_log_path(container_dir):
    """This method created log directory for each container."""
    log_path = os.path.join(container_dir, "logs")
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    return log_path


def change_dir_owner(home, user_name):
    uid = pwd.getpwnam(user_name).pw_uid
    gid = pwd.getpwnam(user_name).pw_gid
    os.system('chown -R {}:{} {}'.format(uid, gid, home))


def prepare_config_file(home, repo, env):
    path = os.path.join(home, repo)
    if env == 'config-dev':
        config_file = os.path.join(path, 'config-dev')
        os.rename(config_file, os.path.join(path, 'config'))


def uid():
    return uuid.uuid4().hex
