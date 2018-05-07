import src.config as settings
from subprocess import call
import syslog

# TODO: Do logging the "correct" way.


class Log(object):

  def __init__(self, jobname, print_terminal=False, asynchronous=False):
    self.jobname = jobname
    self.print_terminal = print_terminal
    # TODO:
    if asynchronous:
      raise Exception('Not implemented yet')

  def set_jobname(self, name):
    self.jobname = name

  def notify_desktop(self, summary, body, persist=False, severe=False):
    if not settings.NotifyDesktop:
      return
    # TODO: Find out what happens on call failure and if we can recover from it.
    stack = ['notify-send', summary, body]
    if not persist:
      stack.append('-t')
      stack.append(settings.NotifyDesktopExpireTime)
    if severe:
      stack.append('-u critical')
    #print('notify command: '+' '.join(stack))
    call(stack)

  def notify_server(self, msg, iserror=False):
    if not settings.NotifyServerLog:
      return
    stack = [
      'ssh', settings.ServerHostname, settings.ServerLogger, 
      '"'+self.jobname+'"', '"'+msg+'"']
    if iserror:
      stack.append('-s 2')
    code = call(stack)
    print('server log code: '+str(code))

  def notify_local(self, msg, iserror=False):
    if not settings.NotifySyslog:
      return
    syslog.openlog(self.jobname)
    syslog.syslog(syslog.LOG_ERR if iserror else syslog.LOG_INFO, msg)

  def notify_all(self, shortmsg, longmsg, iserror=False):
    self.notify_desktop(shortmsg, longmsg, persist=iserror, severe=iserror)
    self.notify_local('%s: %s' % (shortmsg, longmsg), iserror=iserror)
    self.notify_server('%s: %s' % (shortmsg, longmsg), iserror=iserror)
    if self.print_terminal:
      print('%s [%s]: %s: %s', self.jobname, 'ERR' if iserror else 'MSG', shortmsg, longmsg)
