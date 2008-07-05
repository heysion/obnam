# Copyright (C) 2006  Lars Wirzenius <liw@iki.fi>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


"""Obnam configuration and option handling"""


import optparse
import os
import pwd
import socket
import sys

import obnamlib


def default_config():
    """Return a obnamlib.cfgfile.ConfigFile with the default builtin config"""
    config = obnamlib.cfgfile.ConfigFile()
    for section, item, value in obnamlib.defaultconfig.items:
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, item, value)

    if config.get("backup", "host-id") == "":
        config.set("backup", "host-id", socket.gethostname())
    
    return config


def build_parser():
    """Create command line parser"""
    parser = optparse.OptionParser(version="%s %s" % 
                                            (obnamlib.NAME, obnamlib.VERSION))
    
    parser.add_option("--host-id",
                      metavar="ID",
                      help="use ID to identify this host")
    
    parser.add_option("--block-size",
                      type="int",
                      metavar="SIZE",
                      help="make blocks that are about SIZE kilobytes")
    
    parser.add_option("--cache",
                      metavar="DIR",
                      help="store cached blocks in DIR")
    
    parser.add_option("--store",
                      metavar="DIR",
                      help="use DIR for local block storage (not caching)")
    
    parser.add_option("--target", "-C",
                      metavar="DIR",
                      help="resolve filenames relative to DIR")
    
    parser.add_option("--object-cache-size",
                      metavar="COUNT",
                      help="set object cache maximum size to COUNT objects" +
                           " (default depends on block size")
    
    parser.add_option("--log-file",
                      metavar="FILE",
                      help="append log messages to FILE")
    
    parser.add_option("--log-level",
                      metavar="LEVEL",
                      help="set log level to LEVEL, one of debug, info, " +
                           "warning, error, critical (default is warning)")
    
    parser.add_option("--ssh-key",
                      metavar="FILE",
                      help="read ssh private key from FILE (and public key " +
                           "from FILE.pub)")
    
    parser.add_option("--gpg-home",
                      metavar="DIR",
                      help="use DIR as the location for GnuPG keyrings and " +
                           "other data files")
    
    parser.add_option("--gpg-encrypt-to",
                      metavar="KEYID", 
                      action="append",
                      help="add KEYID to list of keys to use for encryption")
    
    parser.add_option("--gpg-sign-with",
                      metavar="KEYID",
                      help="sign backups with KEYID")
    
    parser.add_option("--no-gpg", action="store_true",
                      help="don't use gpg at all")
    
    parser.add_option("--exclude",
                      metavar="REGEXP", 
                      action="append",
                      help="exclude pathnames matching REGEXP")
    
    parser.add_option("--progress",
                      dest="report_progress",
                      action="store_true", default=False,
                      help="report progress when backups are made")
    
    parser.add_option("--generation-times",
                      action="store_true", default=False,
                      help="show generation start/end times " +
                           "with the 'generations' command")
    
    parser.add_option("--no-configs",
                      action="store_true", default=False,
                      help="don't read any configuration files not " +
                           "explicitly named with --config")
    
    parser.add_option("--config",
                      dest="configs",
                      action="append",
                      metavar="FILE",
                      help="also read FILE when reading configuration files")

    return parser


# For unit testing purposes.

_config_file_log = []
def remember_config_file(pathname): _config_file_log.append(pathname)
def forget_config_file_log(): del _config_file_log[:]
def get_config_file_log(): return _config_file_log[:]


def read_config_file(config, filename):
    """Read a config file, if it exists"""
    if os.path.exists(filename):
        f = file(filename)
        config.readfp(f, filename)
        f.close()
        remember_config_file(filename)
    

def parse_options(config, argv):
    """Parse command line arguments and set config values accordingly
    
    This also reads all the default configuration files at the opportune
    moment.
    
    """

    parser = build_parser()
    (options, args) = parser.parse_args(argv)

    paths = []
    if not options.no_configs:
        paths += get_default_paths()
    if options.configs:
        paths += options.configs
    
    for filename in paths:
        read_config_file(config, filename)

    if options.host_id is not None:
        config.set("backup", "host-id", options.host_id)
    if options.block_size is not None:
        config.set("backup", "block-size", "%d" % options.block_size)
    if options.cache is not None:
        config.set("backup", "cache", options.cache)
    if options.store is not None:
        config.set("backup", "store", options.store)
    if options.target is not None:
        config.set("backup", "target-dir", options.target)
    if options.object_cache_size is not None:
        config.set("backup", "object-cache-size", options.object_cache_size)
    if options.log_file is not None:
        config.set("backup", "log-file", options.log_file)
    if options.log_level is not None:
        config.set("backup", "log-level", options.log_level)
    if options.ssh_key is not None:
        config.set("backup", "ssh-key", options.ssh_key)
    if options.gpg_home is not None:
        config.set("backup", "gpg-home", options.gpg_home)
    if options.gpg_encrypt_to is not None:
        config.remove_option("backup", "gpg-encrypt-to")
        for keyid in options.gpg_encrypt_to:
            config.append("backup", "gpg-encrypt-to", keyid)
    if options.gpg_sign_with is not None:
        config.set("backup", "gpg-sign-with", options.gpg_sign_with)
    if options.no_gpg is True:
        config.set("backup", "no-gpg", "true")
    if options.exclude is not None:
        config.remove_option("backup", "exclude")
        for pattern in options.exclude:
            config.append("backup", "exclude", pattern)
    if options.report_progress:
        config.set("backup", "report-progress", "true")
    else:
        config.set("backup", "report-progress", "false")
    if options.generation_times:
        config.set("backup", "generation-times", "true")
    else:
        config.set("backup", "generation-times", "false")

    return args


def print_option_names(f=sys.stdout):
    """Write to stdout a list of option names"""
    # Note that this is ugly, since it uses undocumented underscored
    # attributes, but it's the only way I could find to make it work.
    parser = build_parser()
    for option in parser.option_list:
        for name in option._short_opts + option._long_opts:
            f.write("%s\n" % name)


def write_defaultconfig(config, output=sys.stdout):
    """Write to stdout a new defaultconfig.py, using values from config"""

    items = []
    for section in config.sections():
        for key in config.options(section):
            items.append('  ("%s", "%s", "%s"),' % 
                            (section, key, config.get(section, key)))

    output.write("import socket\nitems = (\n%s\n)\n""" % "\n".join(items))


# Allow unit tests to override default path list.

_default_paths = None
if "default_paths" in dir(obnamlib.defaultconfig):
    _default_paths = obnamlib.defaultconfig.default_paths

def set_default_paths(default_paths):
    global _default_paths
    _default_paths = default_paths


def get_default_paths():
    """Return list of paths to look for config files"""
    
    if _default_paths is not None:
        return _default_paths
    
    list = []

    list.append("/usr/share/obnam/obnam.conf")

    if get_uid() == 0:
        list.append("/etc/obnam/obnam.conf")
    else:
        list.append(os.path.join(get_home(), ".obnam", "obnam.conf"))
        
    return list


# We use a little wrapper layer around the os.* stuff to allow unit tests
# to override things.

_uid = None
_home = None

def get_uid():
    if _uid is None:
        return os.getuid()
    else:
        return _uid
    
def get_home():
    if _home is None:
        return pwd.getpwuid(get_uid()).pw_dir
    else:
        return _home
    
def set_uid_and_home(uid, home):
    global _uid, _home
    _uid = uid
    _home = home