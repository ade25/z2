from fabric.api import cd
from fabric.api import env
from fabric.api import local
from fabric.api import run
from fabric.api import task

from ade25.fabfiles import project
from ade25.fabfiles.server import setup
from ade25.fabfiles.server import controls
from ade25.fabfiles import hotfix as hf

env.use_ssh_config = True
env.forward_agent = True
env.port = '22222'
env.user = 'root'
env.code_user = 'root'
env.prod_user = 'www'
env.webserver = '/opt/webserver/buildout.webserver'
env.code_root = '/opt/webserver/buildout.webserver'
env.host_root = '/opt/sites'

env.hostname = 'z2.ade25.de'
env.server_ip = '5.9.40.61'

env.git_repo = 'git@github.com:ade25/z2.git'

env.host = 'z2'
env.hosts = ['z2']
env.hosted_sites = [
    'example.tld',
]

env.hosted_sites_locations = [
    '/opt/sites/example.tld/buildout.example.tld',
]


@task
def push():
    """ Push committed local changes to git """
    local('git push')


@task
def restart():
    """ Restart all """
    with cd(env.webserver):
        run('nice bin/supervisorctl restart all')


@task
def restart_nginx():
    """ Restart Nginx """
    controls.restart_nginx()


@task
def restart_varnish():
    """ Restart Varnish """
    controls.restart_varnish()


@task
def restart_haproxy():
    """ Restart HAProxy """
    controls.restart_haproxy()


@task
def ctl(*cmd):
    """Runs an arbitrary supervisorctl command."""
    with cd(env.webserver):
        run('nice bin/supervisorctl ' + ' '.join(cmd))


@task
def deploy():
    """ Deploy current master to production server """
    push()
    controls.update()
    controls.build()


@task
def deploy_site():
    """ Deploy a new site to production """
    push()
    controls.update()
    controls.build()
    controls.reload_supervisor()


@task
def hotfix(addon=None):
    """ Apply hotfix to all hosted sites """
    hf.prepare_sites()
    hf.process_hotfix()


@task
def bootstrap():
    """ Bootstrap server and setup the webserver automagically """
    setup.install_system_libs()
    setup.set_hostname()
    setup.configure_fs()
    setup.set_project_user_and_group('www', 'www')
    setup.configure_egg_cache()
    with cd('/opt'):
        setup.install_python()
        setup.generate_virtualenv(sitename='webserver')
    with cd('/opt/webserver'):
        setup.install_webserver()
    setup.setup_webserver_autostart()
