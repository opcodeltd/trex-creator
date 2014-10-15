#!/usr/bin/env python

import os
import subprocess
import argparse
import shutil

trex_creator_root = os.path.dirname(os.path.realpath(__file__))
target_root = None

# To load any more modules, we need to make sure our virtual env is active
if 'VIRTUAL_ENV' not in os.environ or os.environ['VIRTUAL_ENV'] != trex_creator_root:
    activate_this = os.path.join(trex_creator_root, 'bin', 'activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))

import jinja2

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(trex_creator_root, 'templates')))

def parse_cli_args():
    parser = argparse.ArgumentParser(description="Create the working tree for a new trex site")
    parser.add_argument('target', help="Directory to create this project in (shouldn't already exist)")
    parser.add_argument('port', help="Port for the development server to listen on")
    parser.add_argument('--name', '-n', help="Name of this project (used for python module name). Will default to using the basename of the target parameter")
    args = parser.parse_args()

    if not args.name:
        args.name = os.path.basename(args.target).replace('-', '_')

    args.target = os.path.abspath(os.path.expanduser(args.target))

    return args

def copy_file(target_name, mode=None, source_name=None):
    if not source_name:
        source_name = target_name

    target = os.path.join(target_root, target_name)
    source = os.path.join(trex_creator_root, 'templates', source_name)
    shutil.copyfile(source, target)
    if mode:
        os.chmod(target, mode)

def template_file(target_name, args=None, mode=None, source_name=None):
    if not source_name:
        source_name = target_name
    print "templating %s" % target_name
    target = os.path.join(target_root, target_name)
    template = template_env.get_template(source_name)

    open(target, 'w').write(template.render(**args) + "\n")
    if mode:
        os.chmod(target, mode)

if __name__ == "__main__":
    args = parse_cli_args()
    target_root = args.target

    # Create new directory
    if os.path.exists(args.target):
        raise Exception("%s already exists, bailing" % args.target)

    os.mkdir(args.target)
    os.chdir(args.target)
    os.mkdir(os.path.join(target_root, 'app'))
    os.mkdir(os.path.join(target_root, 'node_modules'))
    for new_dir in ['view', 'support', 'templates', 'templates/index', 'cdn', 'cdn/less', 'cdn/js']:
        os.mkdir(os.path.join(target_root, 'app', new_dir))

    # Initialize git
    subprocess.check_call(['git', 'init'])

    # Initialize python virtual environment
    subprocess.check_call(['virtualenv', '-p', 'python2.7', '.'])

    activate_this = os.path.join(target_root, 'bin', 'activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))

    ## Install trex submodule
    subprocess.check_call(['git', 'submodule', 'add', 'git@github.com:shoptime/trex.git', 'trex'])

    os.symlink('../trex/bin/app', 'bin/app')
    os.symlink('../../trex/cdn_overlay', 'app/cdn/trex')

    ## Copy/template files in to place
    template_args = dict(
        name     = args.name,
        basename = os.path.basename(target_root),
        port     = args.port,
    )

    for filename in ['README.md', 'app/default.ini', 'app/local.ini', 'app/local.ini.dist']:
        template_file(filename, template_args)

    for filename in ['site.wsgi', '.gitignore', 'app/__init__.py', 'app/model.py', 'app/view/__init__.py', 'app/view/index.py', 'app/support/auth.py', 'app/templates/base.jinja2', 'app/templates/index/index.jinja2', 'app/support/__init__.py', 'app/cdn/less/app.less']:
        copy_file(filename)

    ## Install dependancies
    subprocess.check_call(['trex/bin/install-deps.sh', '-d'])

    ## Compile static files
    subprocess.check_call(['bin/app', 'compile_static'])

    ## Do the initial commit
    subprocess.check_call(['git', 'add', '-f', 'bin/app'])
    subprocess.check_call(['git', 'add', '.bowerrc', '.gitignore', 'README.md', 'bower.json', 'package.json', 'site.wsgi'])
    subprocess.check_call(['git', 'add', 'app/default.ini', 'app/local.ini.dist', 'app/__init__.py', 'app/cdn/less', 'app/cdn/trex', 'app/model.py', 'app/view', 'app/support', 'app/templates'])
    subprocess.check_call(['git', 'commit', '-m', 'Initial revision'])

    print "Here's a list of things you should probably change:"
    subprocess.check_call(['grep', 'NEW_APP_TODO', '.', '-r', '--color=auto'])
