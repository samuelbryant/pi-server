import sys
import os
import json

import piserver.fileio


_REQUIRED_PROP = '*/*REQUIRED*/*' # used to specify a property as required
# list of properties to read from app config file (name, default value)
_CONFIG_PROPERTIES = [
  ('server_hostname', 'sjb-pi-ext'),
  ('server_data_drive', '/drives/data'),
  ('server_user', 'sambryant'),
  ('server_backup_drive', '/drives/backup'),
  ('rsync_verbose', True),
  ('notify_desktop', True),
  ('notify_server_log', True),
  ('notify_client_log', True),
  ('notify_syslog', True),
  ('notify_desktop_expire_time', 4000)
]

# List of properties to read from job configuration file.
_JOB_CONFIG_PROPERTIES = [
  ('job_name', _REQUIRED_PROP),  # for logging and reporting
  ('run_from', _REQUIRED_PROP),  # can be 'client' or 'server'
  ('source', _REQUIRED_PROP),    # can be 'client' or 'server'
  ('target', _REQUIRED_PROP),    # can be 'client' or 'server'
  ('source_dir', _REQUIRED_PROP),
  ('target_dir', _REQUIRED_PROP),
  ('ignore_files', []),
  ('rsync_delete', False)
  #  ('dryrun', True)
]



class Config(object):

  def __init__(self):
    fname = piserver.fileio.get_app_config_file()

    # read config file
    if not os.path.isfile(fname):
      print('warning: no config file found at %s. using defaults...' % fname)
      config_dict = {}
    else:
      json_file = open(fname, 'r')
      config_dict = json.load(json_file)
      json_file.close()

    for name, default in _CONFIG_PROPERTIES:
      setattr(self, name, config_dict.pop(name, default))
      if getattr(self, name) == _REQUIRED_PROP:
        raise Exception('App config file is missing required property '+name)

    for key, value in config_dict.items():
      print('warning: unused key "%s" found in app config' % (key))

  def print(self):
    print('App-wide config properties:')
    for name, default in _CONFIG_PROPERTIES:
      print('\t%-20s: %s' % (name, str(getattr(self, name))))

  def write(self, fname=None):
    fname = fname or piserver.fileio.get_app_config_file()

    # create parent directory as needed
    if not os.path.isdir(os.path.dirname(fname)):
      os.makedirs(os.path.dirname(fname))

    config_dict = {}
    for name, default in _CONFIG_PROPERTIES:
      config_dict[name] = getattr(self, name, default)

    json_file = open(fname, 'w')
    json_file.write(json.dumps(config_dict, indent=2)+'\n')
    json_file.close()


class JobConfig(object):
  """This object represents the results of reading a job JSON file.

  A job config file is a JSON file that specifies a specific backup job (the job source, dest, etc). It may specify any of the attributes given above in the _JOB_CONFIG_PROPERTIES list. Any attribute not given uses the default specified in the above list.

  In addition, a job config file may override any of the app config settings given in the _CONFIG_PROPERTIES list.
  """

  def __init__(self, jobname, config=None, dryrun=True):
    self.config = config or Config()
    self.dryrun = bool(dryrun)
    self.job_config_name = jobname
    self._overriden_properties = [] # list of app config properties overriden

    fname = piserver.fileio.get_app_job_file(self.job_config_name)

    if not os.path.isfile(fname):
      raise Exception('No job config file found at %s' % fname)
    json_file = open(fname, 'r')
    config_dict = json.load(json_file)
    json_file.close()

    # read job config attributes
    for name, default in _JOB_CONFIG_PROPERTIES:
      setattr(self, name, config_dict.pop(name, default))
      if getattr(self, name) == _REQUIRED_PROP:
        raise Exception(
          'Job config file "%s" is missing required property "%s"' % (
            self.job_config_name, name))

    # read app config overrides
    for name, default in _CONFIG_PROPERTIES:
      if name in config_dict:
        setattr(self.config, name, config_dict.pop(name))
        self._overriden_properties.append(name)

    # print warning for any additional attributes
    for key, value in config_dict.items():
      print('warning: unused key "%s" found in job config "%s"' % (key, self.job_config_name))

  def __getattr__(self, attr):
    """Looks for attributes on global config object before raising error."""
    if hasattr(self.config, attr):
      return getattr(self.config, attr)
    raise AttributeError("'"+str(type(self))+"' has no attribute '"+attr+"'")

  def is_dry_run(self):
    return self.dryrun

  def is_run_from_client(self):
    return self.run_from == 'client'

  def print(self):
    print('Job config properties:')
    for name, default in _JOB_CONFIG_PROPERTIES:
      print('\t%-20s: %s' % (name, str(getattr(self, name))))

  def write(self, fname=None):
    fname = fname or piserver.fileio.get_app_job_file(self.job_config_name)

    # create parent directory as needed
    if not os.path.isdir(os.path.dirname(fname)):
      os.makedirs(os.path.dirname(fname))

    config_dict = {}
    for name, default in _JOB_CONFIG_PROPERTIES:
      config_dict[name] = getattr(self, name, default)

    # also write out overriden app config properties
    for name in self._overriden_properties:
      config_dict[name] = getattr(self.config, name)

    json_file = open(fname, 'w')
    json_file.write(json.dumps(config_dict, indent=2)+'\n')
    json_file.close()

  def gen_rsync_source(self):
    """Generates the appropriate <source> argument to rsync."""
    if self.run_from == 'client':
      if self.source == 'client':
        return self.source_dir
      else:
        raise Exception('job source must match job run-from')
    else:
      if self.source == 'server':
        return self.source_dir
      else:
        raise Exception('job source must match job run-from')

  def gen_rsync_target(self):
    """Generates the appropriate <dest> argument to rsync."""
    if self.run_from == self.target:
      return self.target_dir
    elif self.run_from == 'client' and self.target == 'server':
      return '%s@%s:%s' % (
        self.config.server_user,
        self.config.server_hostname, self.target_dir)
    elif self.run_from == 'server' and self.target == 'client':
      raise Exception('cannot target client when running from server')
    else:
      raise Exception('should never happen')

# class Config(object):
#   """Object representing app-wide configuration."""

#   def __init__(self, config_file=None):
#     """Loads the program config from config_file or the default."""
#     config_file = config_file or piserver.fileio.get_default_app_config_file()

#     config = configobj.ConfigObj(config_file)[_SECTION]



# def write_defaults():
#   config = configobj.ConfigObj()
#   config[_SECTION] = {
#     'server-hostname': 'sjb-pi-ext',
#     'server-user': 'sambryant',
#     'server-data-drive': '/drives/data',
#     'server-backup-drive': '/drives/backup',
#     'client-job-config-dir': '/home/sambryant/.config/piserver/jobs',
#     'client-log-file': '/home/sambryant/.config/piserver/logs/client.log',
#     'server-log-file': '/home/sambryant/.config/piserver/logs/server.log',
#     'rsync-delete': False,
#     'rsync-verbose': True,
#     'notify-desktop': True,
#     'notify-server-log': True,
#     'notify-client-log': True,
#     'notify-syslog': True,
#     'notify-desktop-expire-time': 4000
#   }
#   config.filename = piserver.fileio.get_default_app_config_file()
#   config.write()




# # def load(config_file=None, no_reload=False):
# #   """Loads the program configuration from config_file or the default."""

# #   config_file = config_file or pi_server.fileio.get_app_config_file()


# #   if no_reload and LOADED:
# #     return
# #   config = configobj.ConfigObj(config_file)[DEFAULT_SECTION]
# #   global ClientProjectDir, ServerHostname, ServerLocalname, ServerUser, ServerDataDrive, ServerBackupDrive, ServerLogScript, ServerProjectDir, RsyncDelete, RsyncVerbose, NotifyDesktop, NotifySyslog, NotifyServerLog, NotifyDesktopExpireTime, ServerJobConfigDir, ClientJobConfigDir
# #   ClientJobConfigDir = config['ClientJobConfigDir']
# #   ServerJobConfigDir = config['ServerJobConfigDir']
# #   ClientProjectDir = config['ClientProjectDir']
# #   ServerHostname = config['ServerHostname']
# #   ServerLocalname = config['ServerLocalname']
# #   ServerUser = config['ServerUser']
# #   ServerDataDrive = config['ServerDataDrive']
# #   ServerProjectDir = config['ServerProjectDir']
# #   ServerBackupDrive = config['ServerBackupDrive']
# #   ServerLogScript = config['ServerLogScript']
# #   RsyncDelete = config['RsyncDelete']
# #   RsyncVerbose = config['RsyncVerbose']
# #   NotifyDesktop = config['NotifyDesktop']
# #   NotifySyslog = config['NotifySyslog']
# #   NotifyServerLog = config['NotifyServerLog']
# #   NotifyDesktopExpireTime = config['NotifyDesktopExpireTime']
# #   loaded = True

# # def write_defaults():
# #   config = configobj.ConfigObj()
# #   config[DEFAULT_SECTION] = {
# #     'ClientProjectDir': '/home/sambryant/bin/github_projects/pi-server',
# #     'ServerHostname': 'sjb-pi-ext',
# #     'ServerLocalname': 'sjb-pi',
# #     'ServerUser': 'sambryant',
# #     'ServerDataDrive': '/drives/data',
# #     'ServerBackupDrive': '/drives/backup',
# #     'ServerProjectDir': '/drives/data/pi-server',
# #     'ServerLogScript': 'src/server/log_server.py',
# #     'RsyncDelete': True,
# #     'RsyncVerbose': True,
# #     'NotifyDesktop': True,
# #     'NotifyServerLog': True,
# #     'NotifySyslog': True,
# #     'NotifyDesktopExpireTime': 4000
# #   }
# #   config.filename = CONFIG_FILE
# #   config.write()
# #   #with open('conf.ini', 'w') as configfile:
# #   #  config.write(configfile)

if __name__ == '__main__':
  c = Config()
  c.print()

  if len(sys.argv) == 2:
    j = JobConfig(c, sys.argv[1])
    j.print()

    c.print()
