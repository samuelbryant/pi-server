# In progress. Eventually this will be part of a cron job.
import syslog
import atexit
import os
import src.config as settings
import src.log
from subprocess import call


# TODO:
# These are constants that are specific to each backup set. 
# Eventually these should be dynamically read from a file so this script can
# be reused for many files.
JOBNAME='blade-pi-SNS-backup'
SOURCE_DIR = '/home/sambryant/'
DEST_DIR = '/drives/data/blade/home_sambryant'
IGNORE_FILES = ['/.cache', '/.config/chromium']

# TODO:
# These are global constants that are spcific to the entire pi-server project.
# These should be read from a config file.
#PI_HOST = 'sjb-pi-ext'
#PI_USER = 'sambryant'
#TARGET_DIR = '%s@%s:%s' % (PI_USER, PI_HOST, DEST_DIR)
#'sambryant@sjb-pi-ext:/drives/data/blade/home_sambryant'
#SERVER_LOGGER = 'python3 /drives/data/pi-server/server_scripts/log_server.py'
#OPTIONS = ['-a', '-v', '--delete']
#EXPIRE_TIME = '2000'

def main():
  # Load configuration file
  settings.load()
  settings.set_dryrun(False)

  # Set up logger
  log = src.log.Log(JOBNAME, print_terminal=True, asynchronous=False)

  # First build the rsync command based on config settings:
  rsync_cmd = ['rsync', '-a']
  target = '%s@%s:%s' % (
    settings.ServerUser, settings.ServerHostname, DEST_DIR)
  rsync_cmd.append(SOURCE_DIR)
  rsync_cmd.append(target)
  if settings.DryRun:
    rsync_cmd.append('-n')
  if settings.RsyncDelete:
    rsync_cmd.append('--delete')
  if settings.RsyncVerbose:
    rsync_cmd.append('-v')
  for ignore in IGNORE_FILES:
    rsync_cmd.append('--exclude='+ignore)

  # Add cleanup code in case the script terminates prematurely:
  completed_flag = 0
  def on_exit_cleanup():
    nonlocal completed_flag
    if completed_flag != 1:
      shortmsg = 'Unknown failure during SNS backup'
      longmsg = 'Script terminated prematurely (caught by atexit function.)'
      log.notify_all(shortmsg, longmsg, iserror=True)
  atexit.register(on_exit_cleanup)

  # TODO: add multi-process semaphore locking. To ensure that two backup jobs 
  # dont conflict, we should try to obtain a lock here before doing anything 
  # else.

  # Start backup
  shortmsg = 'SNS backup started'
  longmsg = 'Copying data from %s to %s' % (SOURCE_DIR, target)
  log.notify_all(shortmsg, longmsg)

  print(' '.join(rsync_cmd))
  code = call(rsync_cmd)

  if code == 0:
    shortmsg = 'SNS backup finished successfully'
    longmsg = 'Successfully copied data from %s to %s' % (SOURCE_DIR, target)
    log.notify_all(shortmsg, longmsg)
  else:
    shortmsg = 'SNS backup failed with code %d' % code
    longmsg = 'Failed to backup data from %s to %s\nFailed command: %s' % (
      SOURCE_DIR, target, ' '.join(rsync_cmd))
    log.notify_all(shortmsg, longmsg, iserror=True)
  completed_flag = 1

if __name__ == '__main__':
  main()
