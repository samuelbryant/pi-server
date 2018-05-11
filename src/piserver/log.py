import syslog
import datetime
from subprocess import call
from subprocess import Popen

# TODO: Do logging the "correct" way.



def gen_log_msg(jobname, msg, iserror=False):
  timestamp = datetime.datetime.strftime(
    datetime.datetime.now(), '%y-%m-%d %H:%M:%S')
  msg = '%s [%s] [%s]: %s\n' % (
    timestamp, 'ERR' if iserror else 'MSG', jobname, msg)
  return msg

class Log(object):

  def __init__(self, config, job_config):
    self.config = config
    self.job_config = job_config
    
    client_logging = job_config.run_from_client

    self.notify_desktop = client_logging and config.notify_desktop
    self.notify_syslog = client_logging and config.notify_syslog
    self.notify_client_log = client_logging and config.notify_client_log
    self.notify_server_log = config.notify_server_log

    self.jobname = job_config.job_name
    self.print_terminal = True

  def log(self, shortmsg, longmsg, iserror=False):
    # add dry run tag.
    if self.job_config.dryrun:
      shortmsg = '[DRYRUN] ' + shortmsg

    msg = gen_log_msg(
      self.jobname, '%s: %s' % (shortmsg, longmsg), iserror=iserror)
    
    if self.notify_client_log:
      logf = open(self.config.client_log_file, 'a')
      logf.write(msg)
      logf.close()
    if self.notify_server_log and self.job_config.run_from_client:
      stack = [
        'ssh',
        '%s@%s' % (self.config.server_user, self.config.server_hostname),
        'echo "%s" >> "%s"' % (msg, self.config.server_log_file)]
      Popen(stack)
    if self.notify_server_log and not self.job_config.run_from_client:
      logf = open(self.config.server_log_file, 'a')
      logf.write(msg)
      logf.close()
    if self.notify_desktop:
      stack = ['notify-send', shortmsg, longmsg]
      if iserror:
        stack.append('-u')
        stack.append('critical')
      else:
        stack.append('-t')
        stack.append(self.config.notify_desktop_expire_time)
      Popen(stack) # asynchronous call

  # def notify_client_log(self, msg, iserror=False):
  #   print('notify_client_log placeholder')
  #   pass

  # def notify_desktop(self, summary, body, persist=False, severe=False):
  #   if not self.notify_desktop:
  #     return
  #   if settings.DryRun:
  #     summary = '[DRYRUN] '+summary
  #   # TODO: Find out what happens on call failure and if we can recover from it.
  #   stack = ['notify-send', summary, body]
  #   if not persist:
  #     stack.append('-t')
  #     stack.append(settings.NotifyDesktopExpireTime)
  #   if severe:
  #     stack.append('-u critical')
  #   #print('notify command: '+' '.join(stack))
  #   call(stack)

  # def notify_server(self, msg, iserror=False):
  #   if not settings.NotifyServerLog:
  #     return
  #   if settings.DryRun:
  #     msg = '[DRYRUN] '+msg
  #   stack = [
  #     'ssh', settings.ServerHostname, 'python3 %s/%s' % (settings.ServerProjectDir, settings.ServerLogScript), 
  #     '"'+self.jobname+'"', '"'+msg+'"']
  #   if iserror:
  #     stack.append('-s 2')
  #   code = call(stack)
  #   print('server log code: '+str(code))

  # def notify_local(self, msg, iserror=False):
  #   if not settings.NotifySyslog:
  #     return
  #   if settings.DryRun:
  #     msg = '[DRYRUN] '+msg
  #   syslog.openlog(self.jobname)
  #   syslog.syslog(syslog.LOG_ERR if iserror else syslog.LOG_INFO, msg)

  # def notify_all(self, shortmsg, longmsg, iserror=False):
  #   self.notify_desktop(shortmsg, longmsg, persist=iserror, severe=iserror)
  #   self.notify_local('%s: %s' % (shortmsg, longmsg), iserror=iserror)
  #   self.notify_server('%s: %s' % (shortmsg, longmsg), iserror=iserror)
  #   if self.print_terminal:
  #     print('%s [%s]: %s: %s', self.jobname, 'ERR' if iserror else 'MSG', shortmsg, longmsg)
