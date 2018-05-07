# In progress. Eventually this will be part of a cron job.
import syslog
import atexit
import os
from subprocess import call

DRYRUN = True

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
PI_HOST = 'sjb-pi-ext'
PI_USER = 'sambryant'
TARGET_DIR = '%s@%s:%s' % (PI_USER, PI_HOST, DEST_DIR)
#'sambryant@sjb-pi-ext:/drives/data/blade/home_sambryant'
SERVER_LOGGER = 'python3 /drives/data/pi-server/server_scripts/log_server.py'
OPTIONS = ['-a', '-v', '--delete']
EXPIRE_TIME = '2000'

# Build actual rsync command
rsync_command = ['rsync', SOURCE_DIR, TARGET_DIR]
for option in OPTIONS:
  rsync_command.append(option)
for ignore in IGNORE_FILES:
  rsync_command.append('--exclude='+ignore)
if DRYRUN:
  rsync_command.append('-n')

def notify_desktop(summary, body, persist=False, severe=False):
  # TODO: Find out what happens on call failure and if we can recover from it.
  stack = ['notify-send', summary, body]
  if not persist:
    stack.append('-t')
    stack.append(EXPIRE_TIME)
  if severe:
    stack.append('-u critical')
  #print('notify command: '+' '.join(stack))
  call(stack)

def notify_server(msg, iserror=False):
  stack = ['ssh', PI_HOST, SERVER_LOGGER, '"'+JOBNAME+'"', '"'+msg+'"']
  if iserror:
    stack.append('-s 2')
  code=call(stack)
  print('server logging code: '+str(code))

def notify_local(msg, iserror=False):
  syslog.openlog(JOBNAME)
  syslog.syslog(syslog.LOG_ERR if iserror else syslog.LOG_INFO, msg)

def notify_all(shortmsg, longmsg, iserror=False):
  notify_desktop(shortmsg, longmsg, persist=iserror, severe=iserror)
  notify_local('%s: %s' % (shortmsg, longmsg), iserror=iserror)
  notify_server('%s: %s' % (shortmsg, longmsg), iserror=iserror)

def main():

  # Add cleanup code in case the script terminates prematurely:
  completed_flag = 0
  def on_exit_cleanup():
    nonlocal completed_flag
    if completed_flag != 1:
      shortmsg = 'Unknown failure during SNS backup'
      longmsg = 'Script terminated prematurely (caught by atexit function.)'
      notify_desktop(shortmsg, longmsg, persist=True, severe=True)
      notify_local('\n'.join([shortmsg, longmsg]), iserror=True)
      notify_server('\n'.join([shortmsg, longmsg]), iserror=True)
  atexit.register(on_exit_cleanup)

  # TODO: add multi-process semaphore locking. To ensure that two backup jobs 
  # dont conflict, we should try to obtain a lock here before doing anything 
  # else.

  # Start backup
  shortmsg = 'SNS backup started (dry run = %s)' % str(DRYRUN)
  longmsg = 'Copying data from %s to %s' % (SOURCE_DIR, TARGET_DIR)
  notify_all(shortmsg, longmsg)

  print(' '.join(rsync_command))
  code = call(rsync_command)

  if code == 0:
    shortmsg = 'SNS backup finished successfully (dry run = %s)' % str(DRYRUN)
    longmsg = 'Successfully copied data from %s to %s' % (SOURCE_DIR, TARGET_DIR)
    notify_all(shortmsg, longmsg)
  else:
    shortmsg = 'SNS backup failed with code %d (dry run = %s)' % (code, str(DRYRUN))
    longmsg = 'Failed to backup data from %s to %s\nFailed command: %s' % (
      SOURCE_DIR, TARGET_DIR, ' '.join(rsync_command))
    notify_all(shortmsg, longmsg, iserror=True)
  completed_flag = 1

if __name__ == '__main__':
  user = os.environ['USER']
  syslog.syslog('SJB TEST: sjb-pi: user: '+str(user))
  main()