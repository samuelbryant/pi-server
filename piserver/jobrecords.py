"""Module to record critical information about a job like what its doing, when it starts, did it finish."""
import datetime
import os
import time

import piserver.fileio

STATUS_NOT_STARTED = 0
STATUS_IN_PROGRESS = 1
STATUS_FAILED = 2
STATUS_SUCCESS = 3
STATUS_VALUES = [
  STATUS_NOT_STARTED, STATUS_IN_PROGRESS, STATUS_FAILED, STATUS_SUCCESS
]

def get_master_log_file():
  return os.path.join(piserver.fileio.get_app_job_records_dir(), 'master.log')

def get_master_id_file():
  return os.path.join(piserver.fileio.get_app_job_records_dir(), 'last_id.txt')

def get_job_record_dir(jobid):
  return os.path.join(piserver.fileio.get_app_job_records_dir(), str(jobid))

def get_job_status_file(jobid):
  return os.path.join(get_job_record_dir(jobid), 'status.txt')

def get_job_info_file(jobid):
  return os.path.join(get_job_record_dir(jobid), 'info.txt')

def get_job_log_file(jobid):
  return os.path.join(get_job_record_dir(jobid), 'log.txt')

def get_job_config_file(jobid):
  return os.path.join(get_job_record_dir(jobid), 'job.conf')

def _write_last_id_if_greater(last):
  """Writes the "last job id" to the master record file if its greater than the current "last job id" stored in the master record file."""
  fname = get_master_id_file()
  old = _get_last_id()
  f = open(get_master_id_file(), 'w')
  f.write(str(last)+'\n')
  f.close()

def _get_last_id():
  fname = get_master_id_file()
  if not os.path.exists(fname):
    return 0
  f = open(fname, 'r')
  oid = int(f.read().strip())
  f.close()
  return oid

def _make_new_dir(name):
  if os.path.exists(name): return False
  try:
    os.makedirs(name)
    return True
  except FileExistsError:
    return False

def _get_next_id():
  last = _get_last_id()
  next = last + 1
  while True:
    name = get_job_record_dir(next)
    if _make_new_dir(name):
      break
    next += 1
  _write_last_id_if_greater(next)
  return next

def _get_timestamp():
  return datetime.datetime.strftime(
    datetime.datetime.now(), '%y-%m-%d %H:%M:%S')

def _append_to_log(jobid, msg):
  f = open(get_job_log_file(jobid), 'a')
  f.write('[%s]: %s\n' % (_get_timestamp(), msg))
  f.close()

def _write_status_file(jobid, status, timestamp):
  if not status in STATUS_VALUES:
    raise Exception('Invalid status argument "%s"' % str(status))

  f = open(get_job_status_file(jobid), 'a')
  f.write('%d %s\n' % (status, timestamp))
  f.close()

def _write_master_log_entry(jobid, jobconfig, timestamp, msg):
  msg = '[%s] job %3d [%s]: %s\n' % (timestamp, jobid, jobconfig.job_name, msg)
  f = open(get_master_log_file(), 'a')
  f.write(msg)
  f.close()

def _write_job_info_to_file(file, jobid, jobconfig, timestamp):
  file.write('\tID: %d\n\tJob Name: %s\n\tDryrun: %s\n\tSource: %s: %s\n\tTarget: %s: %s\n\tTime: %s\n' % (
      jobid, jobconfig.job_name, str(jobconfig.is_dry_run()),
      jobconfig.source, jobconfig.source_dir,
      jobconfig.target, jobconfig.target_dir,
      timestamp))

def _write_job_info_file(jobid, jobconfig, timestamp):
  f = open(get_job_info_file(jobid), 'w')
  _write_job_info_to_file(f, jobid, jobconfig, timestamp)
  f.close()

def _write_initial_master_log_entry(jobid, jobconfig, timestamp):
  f = open(get_master_log_file(), 'a')
  f.write('[%s] ******* NEW JOB ID: %d ************\n' % (timestamp, jobid))
  _write_job_info_to_file(f, jobid, jobconfig, timestamp)
  f.close()

def create_new_record(jobconfig):
  """Creates new unique directory to hold information about a job.
  This will return the unique "id" for this job.
  """
  jobid = _get_next_id()
  timestamp = _get_timestamp()
  _write_job_info_file(jobid, jobconfig, timestamp)
  _write_initial_master_log_entry(jobid, jobconfig, timestamp)
  record_initialized(jobid, jobconfig)
  # copy job config to record dir
  jobconfig.write(fname=get_job_config_file(jobid))
  return jobid

def record_initialized(jobid, jobconfig):
  ts = _get_timestamp()
  _write_status_file(jobid, STATUS_NOT_STARTED, ts)
  _write_master_log_entry(jobid, jobconfig, ts, 'initialized')
  record_entry(jobid, 'initialized')

def record_started(jobid, jobconfig):
  ts = _get_timestamp()
  _write_status_file(jobid, STATUS_IN_PROGRESS, ts)
  _write_master_log_entry(jobid, jobconfig, ts, 'started')
  record_entry(jobid, 'started')

def record_success(jobid, jobconfig):
  ts = _get_timestamp()
  _write_status_file(jobid, STATUS_SUCCESS, ts)
  _write_master_log_entry(jobid, jobconfig, ts, 'succeeded')
  record_entry(jobid, 'succeeded')

def record_failure(jobid, jobconfig):
  ts = _get_timestamp()
  _write_status_file(jobid, STATUS_FAILURE, ts)
  _write_master_log_entry(jobid, jobconfig, ts, 'failed')
  record_entry(jobid, 'failed')

def record_call_stack(jobid, stack):
  fixed = [str(s) for s in stack]
  _append_to_log(jobid, 'CALL: '+' '.join(fixed))

def record_entry(jobid, msg):
  print('job %d entry: %s' % (jobid, msg))
  _append_to_log(jobid, msg)
