import sys,os


ENV_TEST_FLAG = 'TEST_PI_SERVER'

def is_test_env():
  return os.environ.get(ENV_TEST_FLAG, '0') == '1'

def _get_user_config_dir():
  if is_test_env() and 'TEST_XDG_CONFIG_HOME' in os.environ:
    return os.environ['TEST_XDG_CONFIG_HOME']
  if 'XDG_CONFIG_HOME' in os.environ:
    return os.environ['XDG_CONFIG_HOME']
  elif 'HOME' in os.environ:
    return os.path.join(os.environ['HOME'], '.config')
  else:
    raise Exception('could not find necessary environment variables')

# Global app stuff
def get_default_app_config_dir():
  return os.path.join(_get_user_config_dir(), 'piserver')

def get_app_config_file(config_dir=None):
  return os.path.join(config_dir or get_default_app_config_dir(), 'app.conf')

# Log file stuff
def get_app_log_dir(config_dir=None):
  return os.path.join(config_dir or get_default_app_config_dir(), 'logs')

def get_app_local_log_file(config_dir=None):
  return os.path.join(get_app_log_dir(config_dir), 'local.log')

def get_app_remote_log_file(config_dir=None):
  return os.path.join(get_app_log_dir(config_dir), 'remote.log')

# Job config stuff
def get_app_job_config_dir(config_dir=None):
  return os.path.join(config_dir or get_default_app_config_dir(), 'jobs')

def get_app_job_file(jobname, config_dir=None):
  if not jobname.endswith('.conf'):
    jobname = jobname + '.conf'
  return os.path.join(get_app_job_config_dir(config_dir), jobname)

def get_user_job_config_files_list(config_dir=None):
  d = get_app_job_config_dir(config_dir=config_dir)
  files = os.listdir(d)
  match = []
  for f in files:
    if f.endswith('.conf'):
      match.append(f)
  return match

# def get_default_app_config_file():
#   return os.path.join(os.environ['HOME'], '.config', 'piserver', 'app.conf')

# def get_job_config_file(config, jobfile):
#   return os.path.join(config.client_job_config_dir, jobfile)

# def get_app_config_file(config):
#   pass

# def get_log_dir(config):
#   pass
