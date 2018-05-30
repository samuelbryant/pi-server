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

def get_master_file():
  return os.path.join(piserver.fileio.get_app_job_records_dir(), 'master.txt')

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
  fname = get_master_file()
  old = _get_last_id()
  f = open(get_master_file(), 'w')
  f.write(str(last)+'\n')
  f.close()

def _get_last_id():
  fname = get_master_file()
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

def _write_job_info(jobid, jobconfig, timestamp):
  f = open(get_job_info_file(jobid), 'w')
  f.write(str(jobid)+'\n')
  f.write(jobconfig.job_name+'\n')
  f.write('%s: %s\n' % (jobconfig.source, jobconfig.source_dir))
  f.write('%s: %s\n' % (jobconfig.target, jobconfig.target_dir))
  f.write(timestamp+'\n')
  f.close()

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

def create_new_record(jobconfig):
  """Creates new unique directory to hold information about a job.
  This will return the unique "id" for this job.
  """
  jobid = _get_next_id()
  timestamp = _get_timestamp()
  _write_job_info(jobid, jobconfig, timestamp)
  _write_status_file(jobid, STATUS_NOT_STARTED, timestamp)
  record_entry(jobid, 'initialized')
  # copy job config to record dir
  jobconfig.write(fname=get_job_config_file(jobid))
  return jobid

def record_started(jobid):
  _write_status_file(jobid, STATUS_IN_PROGRESS, _get_timestamp())
  record_entry(jobid, 'started')

def record_success(jobid):
  _write_status_file(jobid, STATUS_SUCCESS, _get_timestamp())
  record_entry(jobid, 'succeeded')

def record_failure(jobid):
  _write_status_file(jobid, STATUS_FAILURE, _get_timestamp())
  record_entry(jobid, 'failed')

def record_call_stack(jobid, stack):
  fixed = [str(s) for s in stack]
  _append_to_log(jobid, 'CALL: '+' '.join(fixed))

def record_entry(jobid, msg):
  print('job %d entry: %s' % (jobid, msg))
  _append_to_log(jobid, msg)
