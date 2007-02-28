#!/usr/bin/python2.4
#
# Copyright (C) 2007  Lars Wirzenius <liw@iki.fi>
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


"""A FUSE filesystem for backups made with Obnam"""


import errno
import logging
import os
import re
import stat
import sys
import time

import fuse

import obnam


def make_stat_result(st_mode=0, st_ino=0, st_dev=0, st_nlink=0, st_uid=0,
                     st_gid=0, st_size=0, st_atime=0, st_mtime=0, st_ctime=0,
                     st_blocks=0, st_blksize=0, st_rdev=0):

    dict = {
        "st_mode": st_mode,
        "st_ino": st_ino,
        "st_dev": st_dev,
        "st_nlink": st_nlink,
        "st_uid": st_uid,
        "st_gid": st_gid,
        "st_size": st_size,
        "st_atime": st_atime,
        "st_mtime": st_mtime,
        "st_ctime": st_ctime,
        "st_blocks": st_blocks,
        "st_blksize": st_blksize,
        "st_rdev": st_rdev,
    }
    
    tup = (st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size,
           st_atime, st_mtime, st_ctime)

    return os.stat_result(tup, dict)


class ObnamFS(fuse.Fuse):

    """A FUSE filesystem interface to backups made with Obnam"""
    
    def __init__(self, *args, **kw):
        self.context = obnam.context.create()
        argv = obnam.config.parse_options(self.context.config, sys.argv[1:])
        sys.argv = [sys.argv[0]] + argv
        self.context.cache = obnam.cache.init(self.context.config)
        self.context.be = obnam.backend.init(self.context.config, 
                                             self.context.cache)
        obnam.backend.set_progress_reporter(self.context.be, 
                                            self.context.progress)

        fuse.Fuse.__init__(self, *args, **kw)

    def generations(self):
        block = obnam.io.get_host_block(self.context)
        (_, gen_ids, _, _) = obnam.obj.host_block_decode(block)
        return gen_ids

    def getattr(self, path):
        if path == "/":
            return make_stat_result(st_mode=stat.S_IFDIR | 0700, st_nlink=2,
                                    st_uid=os.getuid(), st_gid=os.getgid())
        elif path.startswith("/") and "/" not in path[1:]:
            gen_ids = self.generations()
            if path[1:] in gen_ids:
                return make_stat_result(st_mode=stat.S_IFDIR | 0700,
                                        st_nlink=2,
                                        st_uid=os.getuid(),
                                        st_gid=os.getgid())

        return -errno.ENOENT

    def getdir(self, path):
        if path == "/":
            return [(x, 0) for x in [".", ".."] + self.generations()]
        else:
            return []


def main():
    server = ObnamFS()
    server.main()


if __name__ == "__main__":
    main()
