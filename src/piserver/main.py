# This is the front-end for calling all python programs associated with this 
# python server. Eventually, if the possible functions of this python library
# become too disperse, it may make sense to fractionalize this.
import atexit
import argparse
import os
import sys
import piserver.config
import piserver.jobconfig
import piserver.log
from subprocess import call

PROGRAM = 'pi-server-backup'

class BackupJob(object):
  """Class representing a single backup job."""

  def __init__(self):
    parser = argparse.ArgumentParser(description='pi server backup script')

    # Only required argument is the name of the job file to read from.
    parser.add_argument('jobfile', type=str, help='Job configuration file name (the local name)')

    parser.add_argument('--dryrun', dest='dryrun', action='store_const',
      const=True, default=False,
      help='Sets the dry run flag to true (no data is actually copied)')

    parser.add_argument('--configfile', type=str,
      default=None,
      help='The full path name of the config file to use. By default will use the one stored in the directory chosen during install.')

    args = parser.parse_args(sys.argv[1:])

    # read application and job config files
    self.config = piserver.config.Config(config_file=args.configfile)
    self.job_config = piserver.jobconfig.JobConfig(
      self.config,
      piserver.fileio.get_job_config_file(self.config, args.jobfile),
      args.dryrun)

    # compute the src and dst
    self.src = self.job_config.gen_rsync_source()
    self.dst = self.job_config.gen_rsync_dest()

    # setup logger
    self.log = piserver.log.Log(self.config, self.job_config)

    self.completed = False

    # set up failure catch
    atexit.register(self._failure_catch)

    self._run_backup()

  def _failure_catch(self):
    """Function used to cleanup in case of an unexpected error."""
    if self.completed:
      return
    
    shortmsg = 'piserver backup encountered unknown failure'
    longmsg = 'script terminated prematurely while copying %s to %s' % (self.src, self.dst)
    self.log.log(shortmsg, longmsg, iserror=True)

  def _run_backup(self):
    # first we build the command.
    rsync_cmd = ['rsync', '-a']
    if self.job_config.dryrun:
      rsync_cmd.append('-n')
    if self.job_config.use_delete:
      rsync_cmd.append('--delete')
    if self.job_config.use_verbose:
      rsync_cmd.append('-v')
    for ignore in self.job_config.ignore_files:
      rsync_cmd.append('--exclude='+ignore)
    rsync_cmd.append(self.src)
    rsync_cmd.append(self.dst)

    # start message
    shortmsg = 'piserver backup starting'
    longmsg = 'copying data from %s to %s' % (self.src, self.dst)
    self.log.log(shortmsg, longmsg)

    print('COMMAND: "%s"' % ' '.join(rsync_cmd))
    code = call(rsync_cmd)

    if code == 0:
      shortmsg = 'piserver backup finished successfully'
      longmsg = 'copied data from %s to %s' % (self.src, self.dst)
      self.log.log(shortmsg, longmsg)
    else:
      shortmsg = 'piserver backup failed with code %d' % code
      longmsg = 'failed to copy data from %s to %s' % (self.src, self.dst)
      self.log.log(shortmsg, longmsg, iserror=True)
    self.completed = 1

if __name__ == '__main__':
  print('args: %s' % str(sys.argv))
  BackupJob()
