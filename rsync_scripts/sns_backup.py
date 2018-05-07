# In progress. Eventually this will be part of a cron job.
from subprocess import call

#SOURCE_DIR = '/home/sambryant'
#DEST_DIR = '/media/sambryant/data/blade/home_sambryant'

SOURCE_DIR = '/home/sambryant/'
DEST_DIR = 'sambryant@sjb-pi-ext:/media/sambryant/data/blade/home_sambryant'
LOG_FILE = 'sambryant@sjb-pi-ext:/media/sambryant/data/backup.log'
OPTIONS = ['-a', '-v', '--delete']
IGNORE_FILES = ['/.cache', '/.config/chromium']


def notify_desktop(msg):
  call(['notify-send', 'SNS Backup: ' + msg])

def print_cmd_stack(cmds):
  print(' '.join(cmds))

# First we check that everything exists.


# Next we check lock and assert lock (TODO: Semaphores, posix inter-process)

cmd_stack = ['rsync', SOURCE_DIR, DEST_DIR]

for option in OPTIONS:
  cmd_stack.append(option)
for ignore in IGNORE_FILES:
  cmd_stack.append('--exclude='+ignore)

# Notify desktop
notify_desktop('Starting backup job')
print_cmd_stack(cmd_stack)
return_code = call(cmd_stack)
notify_desktop('Finished backup job')

# print('Finished with code: '+str(return_code))

# Finally we release lock
