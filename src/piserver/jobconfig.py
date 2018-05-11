import configobj
import sys
import os

import piserver.fileio


_SECTION='def'


class JobConfig(object):
  """Class represents the input configuration for a server backup job."""

  def __init__(self, app_config, job_config_file, dryrun):
    if not os.path.exists(job_config_file):
      raise Exception('No job config file found at %s' % job_config_file)


    self.app_config = app_config
    config = configobj.ConfigObj(job_config_file)[_SECTION]

    self.job_name = config['job-name']
    self.run_from = config['run-from'] # can be 'client' or 'server'
    self.source = config['source'] # can be 'client' or 'server'
    self.dest = config['dest'] # can be 'client' or 'server'
    self.source_dir = config['source-dir']
    self.target_dir = config['target-dir']
    self.ignore_files = config['ignore-files'] if 'ignore-files' in config else []
    self.use_delete = config['use-delete'] if 'use-delete' in config else app_config.rsync_delete
    self.use_verbose = config['use-verbose'] if 'use-verbose' in config else app_config.rsync_verbose
    self.dryrun = dryrun
    self.run_from_client = self.run_from == 'client'

    #TODO: validation

  def gen_rsync_source(self):
    """Generates the appropriate <source> argument to rsync."""
    if self.run_from_client:
      if self.source == 'client':
        return self.source_dir
      else:
        raise Exception('job source must match job run-from')
    else:
      if self.source == 'server':
        return self.source_dir
      else:
        raise Exception('job source must match job run-from')

  def gen_rsync_dest(self):
    """Generates the appropriate <dest> argument to rsync."""
    if self.run_from == self.dest:
      return self.target_dir
    elif self.run_from == 'client' and self.dest == 'server':
      return '%s@%s:%s' % (
        self.app_config.server_user,
        self.app_config.server_hostname, self.target_dir)
    elif self.run_from == 'server' and self.dest == 'client':
      raise Exception('cannot target client when running from server')
    else:
      raise Exception('should never happen')

  def write(self, job_config_file):
    config = configobj.ConfigObj()
    config.filename = job_config_file
    config[_Section] = {
      'job-name': self.job_name,
      'source': self.source,
      'dest': self.dest,
      'source-dir': self.source_dir,
      'target-dir': self.target_dir,
      'ignore-files': self.ignore_files,
      'use-delete': self.use_delete,
      'use-verbose': self.use_verbose
    }
    config.write()


def write_defaults():
  c = configobj.ConfigObj()
  c['def'] = {
    'job-name': 'test-job',
    'run-from': 'client',
    'source': 'client',
    'dest': 'server',
    'source-dir': '/home/sambryant/',
    'target-dir': '/drives/data/blade/home_sambryant',
    'ignore-files': ['/.cache', '/.config/chromium'],
    'use-delete': False
  }
  c.filename = '/home/sambryant/.config/piserver/jobs/test'
  c.write()


if __name__ == '__main__':
  write_defaults()