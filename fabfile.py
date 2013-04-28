from fabric.api import task, run, sudo, cd, env
from fabric.contrib.files import exists
system_packages = [
    "wget",
    "axel",
    "abs",
    "base-devel",
    "zsh",
    "git",
    "python2",
    "python2-pip",
    "ruby",
    "zeromq",
    "couchdb",
    "memcached",
    "libmemcached",
    "supervisor"
]

python_packages = [
    "tornado",
    "pylibmc",
    "jsonpickle",
    "pycurl",
    "dateutils",
    "markdown",
    "diff_match_patch",
    "python-openid",
    "gdata",
    "feedgenerator",
    "babel",
    "jinja2",
    "pyzmq",
    "tnetstring",
    "couchapp",
    "IPython",
    "supervisor",
    "py-pretty",
    "pystache"

]

ruby_gems = [
    "compass",
    "susy",
    "fancy-buttons"
]


webapp_path = "~/www/webapps/"
vendor_path = "~/www/var/static/vendor"
git_url = "stevenjoseph.in:~/git"


#env.forward_agent = True


def git_clone_or_update(repo, path):
    if exists(path):
        with cd(path):
            run("git pull origin master")
    else:
        run("git clone %s/%s.git %s" % (git_url, repo, path))
    with cd(path):
        run("git submodule update --init --recursive")


def setup():
    sudo("pacman -S --noconfirm --needed --noprogressbar %s" % " ".join(
        system_packages))
    run("gem install %s" % " ".join(ruby_gems))
    run("pip2 install --install-option='--user' %s"
        % " ".join(python_packages))


def deploy_www():
    git_clone_or_update("server", "~/www/")
    run("mkdir -p " + vendor_path)
    run("mkdir -p " + webapp_path)
    with cd(vendor_path):
        dojo_version = "1.8.3"
        dojo_release_pkg = "dojo-release-%s.tar.gz" % dojo_version
        if not exists(dojo_release_pkg):
            run("axel -a http://download.dojotoolkit.org/release-%s/%s" %
                (dojo_version, dojo_release_pkg))
            run("tar xf %s" % dojo_release_pkg)
        run("ln -sf dojo-release-%s dojo" % dojo_version)


def deploy_app(app):
    print app
    print webapp_path+ app
    git_clone_or_update(app, webapp_path + app)
    with cd(webapp_path + app):
        run("mkdir -p logs")
        run("mkdir -p ")
