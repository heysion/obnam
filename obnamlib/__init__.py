# Copyright (C) 2009  Lars Wirzenius
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


version = '0.10'


import _obnam
from pluginmgr import PluginManager

class AppException(Exception):
    pass

class Error(Exception):
    pass

CHUNK_SIZE = 4096
CHUNK_GROUP_SIZE = 16

from sizeparse import SizeSyntaxError, UnitNameError, ByteSizeParser

from hooks import Hook, HookManager
from cfg import Configuration
from interp import Interpreter
from pluginbase import ObnamPlugin
from vfs import VirtualFileSystem, VfsFactory
from vfs_local import LocalFS
from metadata import (read_metadata, set_metadata, Metadata, metadata_fields,
                      metadata_verify_fields)
from store import Store, LockFail
from forget_policy import ForgetPolicy
from app import App
