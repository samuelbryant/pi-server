import syslog
import datetime
import subprocess

def _notify(summary, body, expire, is_urgent=False):
  stack = ['notify-send', summary, body]
  if is_urgent:
    stack.append('-u')
    stack.append('critical')
  stack.append('-t')
  stack.append(str(expire))
  process = subprocess.Popen(stack) # asynchronous call

def notify_start(jobid, jobconfig):
  if not jobconfig.notify_desktop:
    return
  try:
    summary = 'starting pi server backup job %s (%d)' % (
      jobconfig.job_name, jobid)
    body = 'copying "%s: %s" to "%s: %s"\ndry run: %s' % (
      jobconfig.source, jobconfig.source_dir, jobconfig.target, jobconfig.target_dir,
      str(jobconfig.is_dry_run()))
    _notify(summary, body, jobconfig.notify_desktop_expire_time)
  except Exception as e:
    print('Error: hit exception while trying to show desktop notification. Please debug the desktop notification routine')

def notify_success(jobid, jobconfig):
  if not jobconfig.notify_desktop:
    return
  try:
    summary = 'finished pi server backup job %s (%d)' % (
      jobconfig.job_name, jobid)
    body = 'successfully copied "%s: %s" to "%s: %s"\ndry run: %s' % (
      jobconfig.source, jobconfig.source_dir, jobconfig.target, jobconfig.target_dir,
      str(jobconfig.is_dry_run()))
    _notify(summary, body, jobconfig.notify_desktop_expire_time)
  except Exception as e:
    print('Error: hit exception while trying to show desktop notification. Please debug the desktop notification routine')
def notify_failure(jobid, jobconfig, return_code):
  if not jobconfig.notify_desktop:
    return
  try:
    summary = 'failure during pi server backup job %s (%d)' % (
      jobconfig.job_name, jobid)
    body = 'Encountered error code %s while copying "%s: %s" to "%s: %s"\ndry run: %s' % (str(return_code), jobconfig.source, jobconfig.source_dir, jobconfig.target, jobconfig.target_dir, str(jobconfig.is_dry_run()))
    _notify(summary, body, jobconfig.notify_desktop_expire_time, is_urgent=True)
  except Exception as e:
    print('Error: hit exception while trying to show desktop notification. Please debug the desktop notification routine')
# def notify_start(jobid, jobconfig):
#   pass


# class Log(object):

#   def __init__(self, job_config):
#     self.job_config = job_config

#     client_logging = job_config.is_run_from_client()

#     self.notify_desktop = client_logging and job_config.notify_desktop
#     self.notify_syslog = client_logging and job_config.notify_syslog
#     self.notify_client_log = client_logging and job_config.notify_client_log
#     self.notify_server_log = job_config.notify_server_log

#     self.jobname = job_config.job_name
#     self.print_terminal = True

#   def log(self, shortmsg, longmsg, iserror=False):
#     # add dry run tag.
#     if self.job_config.dryrun:
#       shortmsg = '[DRYRUN] ' + shortmsg

#     msg = gen_log_msg(
#       self.jobname, '%s: %s' % (shortmsg, longmsg), iserror=iserror)

#     if self.notify_client_log:
#       logf = open(piserver.fileio.get_app_local_log_file(), 'a')
#       logf.write(single_end_newline(msg))
#       logf.close()
#     if self.notify_server_log and self.job_config.is_run_from_client():
#       stack = [
#         'ssh',
#         '%s@%s' % (self.job_config.server_user, self.job_config.server_hostname),
#         'printf "%s" >> "%s"' % (
#           single_end_newline(msg), piserver.fileio.get_app_remote_log_file())]
#       Popen(stack)
#     if self.notify_server_log and not self.job_config.is_run_from_client():
#       logf = open(piserver.fileio.get_app_remote_log_file(), 'a')
#       logf.write(single_end_newline(msg))
#       logf.close()
#     if self.notify_desktop:
#       stack = ['notify-send', shortmsg, longmsg]
#       if iserror:
#         stack.append('-u')
#         stack.append('critical')
#       else:
#         stack.append('-t')
#         stack.append(str(self.job_config.notify_desktop_expire_time))
#       Popen(stack) # asynchronous call

#   # def notify_client_log(self, msg, iserror=False):
#   #   print('notify_client_log placeholder')
#   #   pass

#   # def notify_desktop(self, summary, body, persist=False, severe=False):
#   #   if not self.notify_desktop:
#   #     return
#   #   if settings.DryRun:
#   #     summary = '[DRYRUN] '+summary
#   #   # TODO: Find out what happens on call failure and if we can recover from it.
#   #   stack = ['notify-send', summary, body]
#   #   if not persist:
#   #     stack.append('-t')
#   #     stack.append(settings.NotifyDesktopExpireTime)
#   #   if severe:
#   #     stack.append('-u critical')
#   #   #print('notify command: '+' '.join(stack))
#   #   call(stack)

#   # def notify_server(self, msg, iserror=False):
#   #   if not settings.NotifyServerLog:
#   #     return
#   #   if settings.DryRun:
#   #     msg = '[DRYRUN] '+msg
#   #   stack = [
#   #     'ssh', settings.ServerHostname, 'python3 %s/%s' % (settings.ServerProjectDir, settings.ServerLogScript),
#   #     '"'+self.jobname+'"', '"'+msg+'"']
#   #   if iserror:
#   #     stack.append('-s 2')
#   #   code = call(stack)
#   #   print('server log code: '+str(code))

#   # def notify_local(self, msg, iserror=False):
#   #   if not settings.NotifySyslog:
#   #     return
#   #   if settings.DryRun:
#   #     msg = '[DRYRUN] '+msg
#   #   syslog.openlog(self.jobname)
#   #   syslog.syslog(syslog.LOG_ERR if iserror else syslog.LOG_INFO, msg)

  # def notify_all(self, shortmsg, longmsg, iserror=False):
  #   self.notify_desktop(shortmsg, longmsg, persist=iserror, severe=iserror)
  #   self.notify_local('%s: %s' % (shortmsg, longmsg), iserror=iserror)
  #   self.notify_server('%s: %s' % (shortmsg, longmsg), iserror=iserror)
  #   if self.print_terminal:
  #     print('%s [%s]: %s: %s', self.jobname, 'ERR' if iserror else 'MSG', shortmsg, longmsg)
