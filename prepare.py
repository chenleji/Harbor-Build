#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals # We require Python 2.6 or later
from string import Template
import random
import string
import os
import sys
from io import open

#-----------------------------------------------
external_dir = os.getenv('EXTERNAL_DIR')
hostname = os.getenv('HOSTNAME')
ui_url = os.getenv('UI_URL_PROTOCOL') + "://" + hostname
email_server = os.getenv('EMAIL_SERVER')
email_server_port = os.getenv('EMAIL_SERVER_PORT')
email_username = os.getenv('EMAIL_USERNAME')
email_password = os.getenv('EMAIL_PASSWORD')
email_from = os.getenv('EMAIL_FROM')
email_ssl = os.getenv('EMAIL_SSL')
harbor_admin_password = os.getenv('HARBOR_ADMIN_PASSWORD')
auth_mode = os.getenv('AUTH_MODE')
ldap_url = os.getenv('LDAP_URL')
ldap_basedn = os.getenv('LDAP_BASEDN')
db_password = os.getenv('DB_PASSWORD')
self_registration = os.getenv('SELF_REGISTRATION')
customize_crt = os.getenv('CUSTOMIZE_CRT')
crt_country = os.getenv('CRT_COUNTRY')
crt_state = os.getenv('CRT_STATE')
crt_location = os.getenv('CRT_LOCATION')
crt_organization = os.getenv('CRT_ORGANIZATION')
crt_organizationalunit = os.getenv('CRT_ORGANIZATIONALUNIT')
crt_commonname = os.getenv('CRT_COMMONNAME')
crt_email = os.getenv('CRT_EMAIL')
max_job_workers = os.getenv('MAX_JOB_WORKERS')
verify_remote_cert = os.getenv('VERIFY_REMOTE_CERT')
#-----------------------------------------------

ui_secret = ''.join(random.choice(string.ascii_letters+string.digits) for i in range(16))  

base_dir = '/harbor'
templates_dir = '/root/templates'
config_dir = os.path.join(base_dir, "config")
log_dir = os.path.join(base_dir, "log")
storage_dir = os.path.join(base_dir, "storage")
database_dir = os.path.join(base_dir, "database")
crt_file = base_dir + '/cert/' + hostname + '.crt'
key_file = base_dir + '/cert/' + hostname + '.key'

if not os.path.exists(config_dir):
    os.makedirs(os.path.join(base_dir, "config"))

if not os.path.exists(log_dir):
    os.makedirs(os.path.join(base_dir, "log"))

if not os.path.exists(storage_dir):
    os.makedirs(os.path.join(base_dir, "storage"))

if not os.path.exists(database_dir):
    os.makedirs(os.path.join(base_dir, "database"))

ui_config_dir = os.path.join(config_dir,"ui")
if not os.path.exists(ui_config_dir):
    os.makedirs(os.path.join(config_dir, "ui"))

db_config_dir = os.path.join(config_dir, "db")
if not os.path.exists(db_config_dir):
    os.makedirs(os.path.join(config_dir, "db"))

job_config_dir = os.path.join(config_dir, "jobservice")
if not os.path.exists(job_config_dir):
    os.makedirs(job_config_dir)

registry_config_dir = os.path.join(config_dir, "registry")
if not os.path.exists(registry_config_dir):
    os.makedirs(registry_config_dir)

nginx_config_dir = os.path.join(config_dir, "nginx")
if not os.path.exists(nginx_config_dir):
    os.makedirs(nginx_config_dir)

nginx_cert_config_dir = os.path.join(nginx_config_dir, "cert")
if not os.path.exists(nginx_cert_config_dir):
    os.makedirs(nginx_cert_config_dir)

def render(src, dest, **kw):
    t = Template(open(src, 'r').read())
    with open(dest, 'w') as f:
        f.write(t.safe_substitute(**kw))
    print("Generated configuration file: %s" % dest)

ui_conf_env = os.path.join(config_dir, "ui", "env")
ui_conf = os.path.join(config_dir, "ui", "app.conf")
registry_conf = os.path.join(config_dir, "registry", "config.yml")
db_conf_env = os.path.join(config_dir, "db", "env")
job_conf_env = os.path.join(config_dir, "jobservice", "env")
nginx_conf = os.path.join(config_dir, "nginx", "nginx.conf")
nginx_cert_crt = os.path.join(config_dir, "nginx", "cert", hostname+'.crt')
nginx_cert_key = os.path.join(config_dir, "nginx", "cert", hostname+'.key')

conf_files = [ ui_conf, ui_conf_env, registry_conf, db_conf_env, job_conf_env, nginx_conf ]
def rmdir(cf):
    for f in cf:
        if os.path.exists(f):
            print("Clearing the configuration file: %s" % f)
            os.remove(f)
rmdir(conf_files)

render(os.path.join(templates_dir, "ui", "env"),
        ui_conf_env,
        hostname=hostname,
        db_password=db_password,
        ui_url=ui_url,
        auth_mode=auth_mode,
        harbor_admin_password=harbor_admin_password,
        ldap_url=ldap_url,
        ldap_basedn=ldap_basedn,
	    self_registration=self_registration,
        ui_secret=ui_secret,
		verify_remote_cert=verify_remote_cert)

render(os.path.join(templates_dir, "ui", "app.conf"),
        ui_conf,
        email_server=email_server,
        email_server_port=email_server_port,
        email_username=email_username,
        email_password=email_password,
        email_from=email_from,
        email_ssl=email_ssl,
        ui_url=ui_url)

render(os.path.join(templates_dir, "registry", "config.yml"),
        registry_conf,
        ui_url=ui_url)

render(os.path.join(templates_dir, "db", "env"),
        db_conf_env,
        db_password=db_password)

render(os.path.join(templates_dir, "jobservice", "env"),
        job_conf_env,
        db_password=db_password,
        ui_secret=ui_secret,
        max_job_workers=max_job_workers,
        ui_url=ui_url,
        verify_remote_cert=verify_remote_cert)

if os.getenv('UI_URL_PROTOCOL') == 'https':
    src_conf = "nginx-https.conf"
else:
    src_conf = "nginx-http.conf"

render(os.path.join(templates_dir, "nginx", src_conf),
        nginx_conf,
        hostname=hostname)

print("crt_file:%s" % crt_file)
print("key_file:%s" % key_file)
print("nginx_cert_crt:%s" % nginx_cert_crt)
print("nginx_crt_key:%s" % nginx_cert_key)

if os.path.isfile(crt_file): 
    print("check crt_file")
    open(nginx_cert_crt,"wb").write(open(crt_file,"rb").read()) 
if os.path.isfile(key_file): 
    print("check key_file")
    open(nginx_cert_key,"wb").write(open(key_file,"rb").read()) 

def validate_crt_subj(dirty_subj):
    subj_list = [item for item in dirty_subj.strip().split("/") \
        if len(item.split("=")) == 2 and len(item.split("=")[1]) > 0]
    return "/" + "/".join(subj_list)

FNULL = open(os.devnull, 'w')

from functools import wraps
def stat_decorator(func):
    @wraps(func)
    def check_wrapper(*args, **kwargs):
        stat = func(*args, **kwargs)
        message = "Generated configuration file: %s" % kwargs['path'] \
                if stat == 0 else "Fail to generate %s" % kwargs['path']
        print(message)
        if stat != 0:
            sys.exit(1)
    return check_wrapper

@stat_decorator
def check_private_key_stat(*args, **kwargs):
    return subprocess.call(["openssl", "genrsa", "-out", kwargs['path'], "4096"],\
        stdout=FNULL, stderr=subprocess.STDOUT)

@stat_decorator
def check_certificate_stat(*args, **kwargs):
    dirty_subj = "/C={0}/ST={1}/L={2}/O={3}/OU={4}/CN={5}/emailAddress={6}"\
        .format(crt_country, crt_state, crt_location, crt_organization,\
        crt_organizationalunit, crt_commonname, crt_email)
    subj = validate_crt_subj(dirty_subj)
    return subprocess.call(["openssl", "req", "-new", "-x509", "-key",\
        private_key_pem, "-out", root_crt, "-days", "3650", "-subj", subj], \
        stdout=FNULL, stderr=subprocess.STDOUT)

def openssl_is_installed(stat):
    if stat == 0:
        return True
    else:
        print("Cannot find openssl installed in this computer\nUse default SSL certificate file")
        return False

if customize_crt == 'on':
    import subprocess
    shell_stat = subprocess.check_call(["which", "openssl"], stdout=FNULL, stderr=subprocess.STDOUT)
    if openssl_is_installed(shell_stat):
        private_key_pem = os.path.join(config_dir, "ui", "private_key.pem")
        root_crt = os.path.join(config_dir, "registry", "root.crt")
        crt_conf_files = [ private_key_pem, root_crt ]
        rmdir(crt_conf_files)

        check_private_key_stat(path=private_key_pem)
        check_certificate_stat(path=root_crt)

FNULL.close()
print("The configuration files are ready, please use docker-compose to start the service.")

os.system("echo 'appname = jobservice' >> /harbor/config/jobservice/app.conf")
os.system("echo 'runmode = dev' >> /harbor/config/jobservice/app.conf")
os.system("echo '[dev]' >> /harbor/config/jobservice/app.conf")
os.system("echo 'httpport = 80' >> /harbor/config/jobservice/app.conf")

os.system("cp -rf /harbor/config/ui/* /etc/ui/")
os.system("cp -rf /harbor/config/registry/* /etc/registry/")
os.system("cp -rf /harbor/config/jobservice/* /etc/jobservice/")
os.system("cp -rf /harbor/config/nginx/* /etc/nginx/")

print("##Done##")


