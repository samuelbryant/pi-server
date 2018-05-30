"""This is the top level module for my raspberry pi syncing program.

It's definitely more complicated than it needs to be. In short, all it does is
provide a way to run rsync jobs using config files. These would then ideally be
scheduled via cron.

I didn't just pure bash because I want it to be easily modular and configurable
which is tough in bash.

My design intention is not very clear here. I've probably straddled the worst
of both worlds. I've written this application so that it can be configured and
re-installed in other places. But it is also designed around my specific server
client layout and is probably useless to anyone but me. Perhaps the
configurability and re-usability will be useful for me as I change my setup
and get new computers. Regardless, writing the app in this way is a useful
exercise in interacting with the rest of the development world.
"""

import atexit
import argparse
import os
import sys
import subprocess
import piserver.desktop_notify
import piserver.config
import piserver.misc
import piserver.fileio
import piserver.constants
import piserver.jobrecords


def main():
  BackupJob()

def listjobs():
  jobs = piserver.fileio.get_user_job_config_files_list()
  print('Available backup jobs:')
  print('\t'+'\n\t'.join(jobs))

class BackupJob(object):
  """Class representing a single backup job."""

  def __init__(self):
    parser = argparse.ArgumentParser(
      prog=piserver.constants.PROGRAM,
      description=piserver.constants.DESCRIPTION)

    # Only required argument is the name of the job file to read from.
    parser.add_argument('jobname', type=str, help='Job configuration file name (the local name)')

    parser.add_argument(
      '-v', '--version', action='version',
      version='%(prog)s ' + piserver.constants.__version__)

    parser.add_argument('--dryrun', dest='dryrun', action='store_const',
      const=True, default=False,
      help='Sets the dry run flag to true (no data is actually copied)')

    args = parser.parse_args(sys.argv[1:])

    # read application and job config files
    self.job_config = piserver.config.JobConfig(
      args.jobname, dryrun=args.dryrun)

    # compute the src and dst
    self.src = self.job_config.gen_rsync_source()
    self.dst = self.job_config.gen_rsync_target()

    # setup job records
    self.jobid = piserver.jobrecords.create_new_record(self.job_config)
    # # setup logger
    # self.log = piserver.log.Log(self.job_config)

    self.completed = False

    # set up failure catch
    atexit.register(self._failure_catch)

    self._run_backup()

  def _failure_catch(self):
    """Function used to cleanup in case of an unexpected error."""
    if self.completed:
      return

    piserver.desktop_notify.notify_failure(self.jobid, self.job_config, '?')
    piserver.jobrecords.record_failure(self.jobid, self.job_config)
    piserver.jobrecords.record_entry('failure was caught by _failure_catch')
    # shortmsg = 'piserver backup encountered unknown failure'
    # longmsg = 'script terminated prematurely while copying %s to %s' % (self.src, self.dst)
    # self.log.log(shortmsg, longmsg, iserror=True)

  def _run_backup(self):
    # first we build the command.
    rsync_cmd = ['rsync', '-a']
    if self.job_config.is_dry_run():
      rsync_cmd.append('-n')
    if self.job_config.rsync_delete:
      rsync_cmd.append('--delete')
    if self.job_config.rsync_verbose:
      rsync_cmd.append('-v')
    for ignore in self.job_config.ignore_files:
      rsync_cmd.append('--exclude='+ignore)
    rsync_cmd.append(self.src)
    rsync_cmd.append(self.dst)

    # start record
    piserver.jobrecords.record_started(self.jobid, self.job_config)
    piserver.jobrecords.record_call_stack(self.jobid, rsync_cmd)
    piserver.desktop_notify.notify_start(self.jobid, self.job_config)

    # # start message
    # shortmsg = 'piserver backup starting'
    # longmsg = 'copying data from %s to %s' % (self.src, self.dst)
    # self.log.log(shortmsg, longmsg)
    # print('CALL: '+' '.join(rsync_cmd))
    code = subprocess.call(rsync_cmd)

    if code == 0:
      piserver.jobrecords.record_success(self.jobid, self.job_config)
      piserver.desktop_notify.notify_success(self.jobid, self.job_config)
      # shortmsg = 'piserver backup finished successfully'
      # longmsg = 'copied data from %s to %s' % (self.src, self.dst)
      # self.log.log(shortmsg, longmsg)
    else:
      piserver.jobrecords.record_failure(self.jobid, self.job_config)
      piserver.desktop_notify.notify_failure(self.jobid, self.job_config, code)
      piserver.jobrecords.record_entry(
        self.jobid, 'subprocess failed with code %d' % code)
      # shortmsg = 'piserver backup failed with code %d' % code
      # longmsg = 'failed to copy data from %s to %s' % (self.src, self.dst)
      # self.log.log(shortmsg, longmsg, iserror=True)
    self.completed = 1

if __name__ == '__main__':
  main()
