# -*- coding: utf-8 -*-
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping
import yaml
import io
import os


class Config(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._data = dict()
        self._data.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    @classmethod
    def from_envvar(cls, env):
        """Create configuration object from an environment variable.

        Environment variable should point to a YAML file.

        :param env: environment variable
        """
        with io.open(os.getenv(env)) as fh:
            cfg = yaml.load(fh)
            return cls(cfg)
