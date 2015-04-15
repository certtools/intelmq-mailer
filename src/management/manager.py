# Insert path to make sure we can load the other modules
import os
import sys
base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, base_path)

# Global imports
from crontab import CronTab
from ConfigParser import ConfigParser

# Local imports
from management.utils import *
from lib.logger import *

class ReportDaemon:
    def __init__(self):
        self.cron = CronTab()

        self.base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.reports_path = os.path.join(self.base_path, 'reports')
        self.mailer_path = os.path.join(self.base_path, 'mailer')
        self.management_path = os.path.join(self.base_path, 'management')
        self.log_path = os.path.join(self.base_path, 'logs')
        self.mailer_script = os.path.join(self.mailer_path, 'mailer.py')
        self.main_script = os.path.join(self.management_path, 'manager.py')
        self.system_config = os.path.join(self.base_path, 'intelmailer.conf')

        self.config = ConfigParser(allow_no_value=True)
        self.config.read(self.system_config)
        
        self.logger = create_logger_main(self.config.get('log', 'path'))

    def reload_configs(self):
        self.logger.info('Reloading configurations')
        # For each config file in the reports path find a crontab job that references it and see if the content hasn't changed
        for conffile in os.listdir(self.reports_path):
            if not conffile.endswith('.report'):
                continue

            fullpath_conffile = os.path.join(self.reports_path, conffile)
            job = find_report(self.cron, fullpath_conffile)
            if get_job_contents_hash(job) != get_report_contents_hash(fullpath_conffile):
                remove_report(self.cron, job)
                add_report(self.cron, self.mailer_script, fullpath_conffile, self.system_config)
                self.logger.info('Adding new report: ' + fullpath_conffile)

    def start(self):
        self.logger.info('Starting report manager')
        self.reload_configs()
        create_main_job(self.cron, self.main_script)

    def stop(self):
        self.logger.info('Stopping report manager')
        delete_all_jobs(self.cron)

if __name__ == "__main__":
    daemon = ReportDaemon()
    try:
        if len(sys.argv) == 2:
            if sys.argv[1] == 'start':
                daemon.start()
            elif sys.argv[1] == 'stop':
                daemon.stop()
            elif sys.argv[1] == 'reload':
                daemon.reload_configs()
            else:
                daemon.logger.error('Call with start/stop/reload')
                print 'Call with start/stop/reload'
        else:
            daemon.reload_configs()
    except Exception, e:
           daemon.logger.critical(repr(e))
        
# Regex to split values: re.split('(.*?[^\\\\]),', b) carefully check for blanks

