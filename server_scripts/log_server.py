import syslog
import sys
import argparse
# Script used to make log entries on the server
# This should be called using SSH from the client. e.g.:
#  ssh sjb-pi-ext .../log_server.py <job name> <msg>


USAGE = '(ssh sjb-pi-ext python3) log_server.py <jobname> <message>'


def main():
  parser = argparse.ArgumentParser(
    description='Log to server\'s syslog from client', usage=USAGE)
  parser.add_argument(
      'jobname', type=str, help='The jobname to identify entries in syslog')
  parser.add_argument(
      'message', type=str, help='The message to log in server\'s syslog')
  args = parser.parse_args(sys.argv[1:])

  syslog.openlog(args.jobname)
  syslog.syslog(args.message)
  exit(0)



