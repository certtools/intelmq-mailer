import re
import hashlib
from ConfigParser import ConfigParser

CRONTAB_LIB_ID = "intelmailer: "
CRONTAB_REPORT_RELOAD = '*/5 * * * *'

def create_main_job(cron, main_script):
    job = cron.new(command='python ' + main_script + ' reload', comment=CRONTAB_LIB_ID + 'check new reports cycle')
    job.setall(CRONTAB_REPORT_RELOAD)
    cron.write()

def delete_main_job(cron):
    jobs = cron.find_comment(CRONTAB_LIB_ID + 'check new reports cycle')
    for job in jobs:
        cron.remove(job)
    cron.write()

def delete_all_jobs(cron):
    jobs_to_remove = list()
    for job in cron:
        if job.comment.startswith(CRONTAB_LIB_ID):
            jobs_to_remove.append(job)

    # Done in two steps because if we call remove inside the loop it stops
    for job in jobs_to_remove:
        cron.remove(job)
    cron.write()

def load_config(report_filename):
    config = ConfigParser(allow_no_value=True)
    config.read(report_filename)
    return config

def get_report_contents_hash(report_filename):
    hash_engine = hashlib.sha512()
    report = open(report_filename, 'r')
    hash_engine.update(report.read())
    return hash_engine.hexdigest()

def get_report_filename_hash(report_filename):
    hash_engine = hashlib.sha512()
    hash_engine.update(report_filename)
    return hash_engine.hexdigest()

def get_job_contents_hash(job):
    if job == None:
        return None

    results = re.findall('%s[0-9a-fA-F]+:([0-9a-fA-F]+)' % CRONTAB_LIB_ID, job.comment)

    if len(results) == 1:
        return results[0]
    else:
        return None

def find_report(cron, report_filename):
    report_filename_hash = get_report_filename_hash(report_filename)
    starts_with = '%s%s:' % (CRONTAB_LIB_ID, report_filename_hash)

    for job in cron:
        if job.comment.startswith(starts_with):
            return job

def prepare_time(report_config):
    return report_config.get('general', 'schedule')

def prepare_command(report_script, report_filename, system_config):
    return 'python %s %s %s' % (report_script, report_filename, system_config)

def prepare_comment(report_filename):
    return "%s%s:%s" % (CRONTAB_LIB_ID, get_report_filename_hash(report_filename), get_report_contents_hash(report_filename))

def create_job_from_config(report_script, report_filename, system_config):
    report_config = load_config(report_filename)

    comment = prepare_comment(report_filename)
    command = prepare_command(report_script, report_filename, system_config)
    time = prepare_time(report_config)

    return (command, comment, time)

def remove_report(cron, job):
    if job is not None and cron is not None:
        cron.remove(job)

def add_report(cron, report_script, report_filename, system_config):
    (command, comment, time) = create_job_from_config(report_script, report_filename, system_config)
    job = cron.new(command=command, comment=comment)
    job.setall(time)
    cron.write()
