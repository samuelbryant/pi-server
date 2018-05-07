import syslog
import sys
import argparse
import time
import datetime
# Script used to make log entries on the server
# This should be called using SSH from the client. e.g.:
#  ssh sjb-pi-ext .../log_server.py <job name> <msg>

USAGE = '(ssh sjb-pi-ext python3) log_server.py <jobname> <message>'

# rasp pi doesn't have a syslog by default so we will use our own log.
LOG_FILE = '/drives/data/logs/backup_info.log'
ERR_FILE = '/drives/data/logs/backup_fail.log'

SEVERITY_LABELS = {
  0: 'MSG',
  1: 'WRN',
  2: 'ERR'
}

def main():
  parser = argparse.ArgumentParser(
    description='Log to server\'s syslog from client', usage=USAGE)
  parser.add_argument(
      'jobname', type=str, help='The jobname to identify entries the log')
  parser.add_argument(
      'message', type=str, help='The message to log in server side log')
  parser.add_argument(
      '-s', dest='severity', type=int, choices=[0,1,2],
      default=0,
      help='Severity level of log entry (0 = message, 1 = warning, 2 = error)')
  args = parser.parse_args(sys.argv[1:])


  timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%y-%m-%d %H:%M:%S')

  msg = '%s [%s] [%s]: %s\n' % (
    timestamp, SEVERITY_LABELS[args.severity], args.jobname, args.message)

  logf = open(LOG_FILE, 'a')
  logf.write(msg)
  logf.close()

  if args.severity != 0:
    errf = open(ERR_FILE, 'a')
    errf.write(msg)
    errf.close()

  exit(0)

if __name__ == '__main__':
  main()
