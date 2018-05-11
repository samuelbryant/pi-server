import configobj
import sys
import os

import piserver.fileio

_SECTION='DEFAULT'

class Config(object):
  """Object representing app-wide configuration."""

  def __init__(self, config_file=None):
    """Loads the program config from config_file or the default."""
    config_file = config_file or piserver.fileio.get_default_app_config_file()

    config = configobj.ConfigObj(config_file)[_SECTION]


    self.server_hostname = config['server-hostname']
    self.server_user = config['server-user']
    self.server_data_drive = config['server-data-drive']
    self.server_log_file = config['server-log-file']
    self.server_backup_drive = config['server-backup-drive']
    self.client_job_config_dir = config['client-job-config-dir']
    self.client_log_file = config['client-log-file']
    self.rsync_delete = config['rsync-delete']
    self.rsync_verbose = config['rsync-verbose']
    self.notify_desktop = config['notify-desktop']
    self.notify_syslog = config['notify-syslog']
    self.notify_server_log = config['notify-server-log']
    self.notify_client_log = config['notify-client-log']
    self.notify_desktop_expire_time = config['notify-desktop-expire-time']

def write_defaults():
  config = configobj.ConfigObj()
  config[_SECTION] = {
    'server-hostname': 'sjb-pi-ext',
    'server-user': 'sambryant',
    'server-data-drive': '/drives/data',
    'server-backup-drive': '/drives/backup',
    'client-job-config-dir': '/home/sambryant/.config/piserver/jobs',
    'client-log-file': '/home/sambryant/.config/piserver/logs/client.log',
    'server-log-file': '/home/sambryant/.config/piserver/logs/server.log',
    'rsync-delete': False,
    'rsync-verbose': True,
    'notify-desktop': True,
    'notify-server-log': True,
    'notify-client-log': True,
    'notify-syslog': True,
    'notify-desktop-expire-time': 4000
  }
  config.filename = piserver.fileio.get_default_app_config_file()
  config.write()




# def load(config_file=None, no_reload=False):
#   """Loads the program configuration from config_file or the default."""

#   config_file = config_file or pi_server.fileio.get_app_config_file()


#   if no_reload and LOADED:
#     return
#   config = configobj.ConfigObj(config_file)[DEFAULT_SECTION]
#   global ClientProjectDir, ServerHostname, ServerLocalname, ServerUser, ServerDataDrive, ServerBackupDrive, ServerLogScript, ServerProjectDir, RsyncDelete, RsyncVerbose, NotifyDesktop, NotifySyslog, NotifyServerLog, NotifyDesktopExpireTime, ServerJobConfigDir, ClientJobConfigDir
#   ClientJobConfigDir = config['ClientJobConfigDir']
#   ServerJobConfigDir = config['ServerJobConfigDir']
#   ClientProjectDir = config['ClientProjectDir']
#   ServerHostname = config['ServerHostname']
#   ServerLocalname = config['ServerLocalname']
#   ServerUser = config['ServerUser']
#   ServerDataDrive = config['ServerDataDrive']
#   ServerProjectDir = config['ServerProjectDir']
#   ServerBackupDrive = config['ServerBackupDrive']
#   ServerLogScript = config['ServerLogScript']
#   RsyncDelete = config['RsyncDelete']
#   RsyncVerbose = config['RsyncVerbose']
#   NotifyDesktop = config['NotifyDesktop']
#   NotifySyslog = config['NotifySyslog']
#   NotifyServerLog = config['NotifyServerLog']
#   NotifyDesktopExpireTime = config['NotifyDesktopExpireTime']
#   loaded = True

# def write_defaults():
#   config = configobj.ConfigObj()
#   config[DEFAULT_SECTION] = {
#     'ClientProjectDir': '/home/sambryant/bin/github_projects/pi-server',
#     'ServerHostname': 'sjb-pi-ext',
#     'ServerLocalname': 'sjb-pi',
#     'ServerUser': 'sambryant',
#     'ServerDataDrive': '/drives/data',
#     'ServerBackupDrive': '/drives/backup',
#     'ServerProjectDir': '/drives/data/pi-server',
#     'ServerLogScript': 'src/server/log_server.py',
#     'RsyncDelete': True,
#     'RsyncVerbose': True,
#     'NotifyDesktop': True,
#     'NotifyServerLog': True,
#     'NotifySyslog': True,
#     'NotifyDesktopExpireTime': 4000
#   }
#   config.filename = CONFIG_FILE
#   config.write()
#   #with open('conf.ini', 'w') as configfile:
#   #  config.write(configfile)

if __name__ == '__main__':
  write_defaults()