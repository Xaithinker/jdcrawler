# -*- coding:utf-8 -*-

from collections.abc import Mapping
from . import setting
from importlib import import_module
import logging
import types
import json
import copy


logger = logging.getLogger('USER_SETTINGS')
logger.setLevel(logging.INFO)

class BaseSettings(object):
    """
    store setting
    and using .get() to get the default arrribute
    .set() to update the setting
    """
    def __init__(self):
        self.attribute = {}
    
    def __getitem__(self, opt_name):
        """get value of attribute"""
        if opt_name not in self:
            return None
        return self.attribute[opt_name]
    
    def __contains__(self, opt_name):
        return opt_name in self.attribute

    def __len__(self):
        return len(self.attribute)
    
    def __iter__(self):
        return iter(self.attribute)
    
    def __delitem__(self, name):
        logger.warning(f"Delete attribute: {name}={self.attribute[name]}")
        del self.attribute[name]
    
    def get(self, name, default=None):
        return self[name] if name in self else  default
    
    def getbool(self, name, default=False):
        got = self.get(name, default)
        try:
            return bool(int(got))
        except ValueError:
            if got in ('True', 'true'):
                return True
            if got in ('False', 'false'):
                return False
    def getint(self, name, default=0):
        return int(self.get(name, default))
    
    def getfloat(self, name, default=0.0):
        return float(self.get(name, default))
    
    def getlist(self, name, default=None):
        value = self.get(name, default or [])
        if isinstance(value, str):
            value = value.split(',')
        return list(value)
    
    def _set(self, module):
        if isinstance(module, str):
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.attribute[key] = getattr(module, key)

class Settings(BaseSettings):

    def __init__(self):
        super(Settings, self).__init__()
 
    @classmethod
    def copy(cls, moudle):
        self = cls()
        self._set(moudle)
        return copy.deepcopy(self)