
import json
import os

config_file = os.getenv('CONFIG_FILE')
if not config_file:
  raise EnvironmentError('missing CONFIG_FILE environemnt variable')
if not os.path.isfile(config_file):
  raise EnvironmentError('CONFIG_FILE={!r} does not exist'.format(config_file))

with open(config_file) as fp:
  config = json.load(fp)


def get(key, default=NotImplemented):
  parts = key.split('.')
  value = config
  for part in parts:
    try:
      if not isinstance(value, dict):
        raise KeyError
      value = value[part]
    except KeyError:
      if default is NotImplemented:
        raise KeyError(key)
      return default
  return value
