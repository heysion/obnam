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


'''Hooks with callbacks.

In order to de-couple parts of the application, especially when plugins
are used, hooks can be used. A hook is a location in the application
code where plugins may want to do something. Each hook has a name and
a list of callbacks. The application defines the name and the location
where the hook will be invoked, and the plugins (or other parts of the
application) will register callbacks.

'''


class Hook(object):

    '''A hook.'''

    def __init__(self, name):
        self.name = name
        self.callbacks = []
        
    def add_callback(self, callback):
        if callback not in self.callbacks:
            self.callbacks.append(callback)
        return callback
        
    def call_callbacks(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)
        
    def remove_callback(self, callback_id):
        if callback_id in self.callbacks:
            self.callbacks.remove(callback_id)


class HookManager(object):

    '''Manage the set of hooks the application defines.'''
    
    def __init__(self):
        self.hooks = {}
        
    def new(self, name):
        pass

    def add_callback(self, name, callback):
        pass
        
    def remove_callback(self, name, callback_id):
        pass
        
    def call(self, name, *args, **kwargs):
        pass

