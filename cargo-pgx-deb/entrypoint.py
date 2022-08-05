#!/bin/python3

# Build a single Debian package using PGX and cargo. This is a very
# basic build and we should refine this to use something like
# git-buildpackage instead, which can handle both Debian and RPM
# packages.
#
# The packages are built and placed in the working directory of the
# GitHub workflow, typically in the debian directory.
#
# We are using format string listerals quite heavily, which might be
# good to move away from and make more generic.
#
# The following environment variables need to be passed and should be
# set in the ``action.yml`` specification based on input parameters:
#
# PACKAGE: The package name
#
# VERSION: The package version in the form major.minor.patch
# 
# DESCRIPTION: A description text for the package. It will be wrapped
#     if necessary.
#
# ARCH: Architecture, typically found by calling "uname -m", but note
#     that we can only use names available in "dpkg-architecture -L",
#     so you need to translate to an architecture on the list.
#
# MAINTAINER: Name and e-mail of the maintainer
#
# HOMEPAGE_URL: The URL of the homepage for the package.
#
# DEPENDS: Dependencies as a comma-separated list of dependencies.
#
# OS_NAME: Name of the operating system or distro. If not set, output
#     of "lsb_release -si" will be used.
#
# OS_VERSION: Version of the operating system or distro. If not set,
#     output of "lsb_release -sr" will be used.
#
# PATH: The path need to include the ``pg_config`` to use when
#     building. It will be used to figure out the PostgreSQL version
#     that we are building for.

import os
import sys
import re
import glob
import shutil
import subprocess
from subprocess import getoutput


def make_control_file():
    """Make the Debian control file.

    We should probably use dh_make to create all the debian files instead.

    """
    with open("debian/control", "w") as f:
        f.write(f"""\
Source: {PACKAGE}
Maintainer: {MAINTAINER}
Homepage: {HOMEPAGE_URL}
Rules-Requires-Root: no
Section: database
Priority: extra
Build-Depends: debhelper-compat (= 12)

Package: {PACKAGE}
Architecture: {ARCH}
Depends: {DEPENDS}
Description: {DESCRIPTION}
""")


def make_changelog_file():
    """Make the Debian Changelog file.

    We should probably use dh_make to create all the debian files instead.
    """
    with open("debian/changelog", "w") as f:
        f.write(f"""\
{PACKAGE} (1:{DEB_VERSION}) unused; urgency=medium

  * See https://github.com/timescale/timescaledb-toolkit/releases

 -- {MAINTAINER}  {DATE}
""")


def make_rules_file():
    """Make the debian/rules file.

    Very simplistic version.
    """

    subprocess.run(["ln", "-s", "/usr/bin/dh", "debian/rules"], check=True)


def make_install_file():
    """Make the install file.
    """
    with open(f"debian/install", "w") as f:
        f.write(f"{TREE}/usr/* usr/\n")

def build_package():
    """Build the package.
    """
    package_dir = '_packages'
    
    subprocess.run([
        "dpkg-buildpackage", "--build=binary", "--no-sign", "--post-clean",
    ], check=True)

    # Move all build artifacts to the _package directory relative to
    # working directory. Since this is running inside a docker
    # container, we need to write to the current directory or below.
    os.mkdir(package_dir)
    for fname in glob.glob(f'../{PACKAGE}*'):
        print(f"Moving {fname} to {package_dir}")
        shutil.move(fname, package_dir)


REQUIRED = (
    'ARCH',
    'DESCRIPTION',
    'HOMEPAGE_URL',
    'MAINTAINER',
    'PACKAGE',
    'VERSION',
)

if __name__ == '__main__':
    # Check for required environment variables.
    unset = [v for v in REQUIRED if v not in os.environ or not os.environ[v]]
    if len(unset) > 0:
        for var in unset:
            print(f"{var} not set")
        sys.exit(2)

    # Start setting global variables with the values we want: we use
    # formatting literal strings heavily.
    ARCH = os.environ['ARCH']
    DEPENDS = os.environ.get('DEPENDS') or ''
    DESCRIPTION = os.environ.get('DESCRIPTION')
    HOMEPAGE_URL = os.environ['HOMEPAGE_URL']
    MAINTAINER = os.environ['MAINTAINER']
    PACKAGE = os.environ['PACKAGE']
    VERSION = os.environ['VERSION']
    TREE = os.environ['TREE']

    # Compute some defaults if they do not exist.
    OS_NAME = (os.environ.get('OS_NAME')
               or getoutput("lsb_release -si").lower())
    OS_RELEASE = (os.environ.get('OS_NAME')
                  or getoutput("lsb_release -sr").lower())

    DATE = getoutput("TZ=Etc/UTC date -R")

    # Figure out the PostgreSQL version using pg_config
    pg_version = getoutput("pg_config --version")
    mobj = re.match(r'PostgreSQL (\d+)\.(\d+)', pg_version)
    if mobj:
        PG_MAJOR = mobj.group(1)
        PG_MINOR = mobj.group(2)
    else:
        sys.exit(f"bad format '{pg_version}' of PostgreSQL version")
    DEB_VERSION = f"{VERSION}~{OS_NAME}{OS_RELEASE}"

    # This generation is very simplistic, we should probably use
    # dh_make(1) here instead and start from there.
    os.mkdir('debian')
    make_rules_file()
    make_control_file()
    make_changelog_file()
    make_install_file()
    build_package()
