import syslog
import sys
# Script used to make log entries on the server
# This should be called using SSH from the client. e.g.:
#  ssh sjb-pi-ext:/.../log_server.py <job name> <msg>


USAGE = 'ssh sjb-pi-ext python3 log_server.py <job name> <msg>'



for arg in sys.argv:
  print('Arg: '+str(arg))

