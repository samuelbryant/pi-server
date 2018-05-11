import sys,os


def get_default_app_config_file():
  return os.path.join(os.environ['HOME'], '.config', 'piserver', 'app.conf')


def get_job_config_file(config, jobfile):
  return os.path.join(config.client_job_config_dir, jobfile)

def get_app_config_file(config):
  pass

def get_log_dir(config):
  pass