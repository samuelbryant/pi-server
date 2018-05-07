# In progress. Eventually this will be part of a cron job.
import syslog
from subprocess import call

JOBNAME='pi-SNS-backup'

SOURCE_DIR = '/home/sambryant/'
DEST_DIR = 'sambryant@sjb-pi-ext:/drives/data/blade/home_sambryant'
OPTIONS = ['-a', '-v', '--delete']
IGNORE_FILES = ['/.cache', '/.config/chromium']

def open_log():
  syslog.openlog(JOBNAME)

def write_to_log(msg):
  syslog.syslog(msg)

def notify_desktop(msg):
  call(['notify-send', 'SNS Backup: ' + msg])

def print_cmd_stack(cmds):
  print(' '.join(cmds))

cmd_stack = ['sudo', 'rsync', SOURCE_DIR, DEST_DIR]

for option in OPTIONS:
  cmd_stack.append(option)
for ignore in IGNORE_FILES:
  cmd_stack.append('--exclude='+ignore)

# First we check that everything exists.


# Next we check lock and assert lock (TODO: Semaphores, posix inter-process)


# Notify desktop
notify_desktop('Starting backup job')
write_to_log('starting SNS backup job')
print_cmd_stack(cmd_stack)
return_code = call(cmd_stack)
write_to_log('finished SNS backup job with code '+str(return_code))
notify_desktop('Finished backup job with code '+str(return_code))

# print('Finished with code: '+str(return_code))

# Finally we release lock
