# For each report save the following state:
#    - config
#    - first run
#    - last run
#    - next run
#    - 
import os
from ConfigParser import RawConfigParser

from lib.state import ReportState
from threading import Timer
from lib.logger import *
from management.utils import *

RELOAD_DELAY = 10

class ReportDaemon(object):
    reports = dict()
    
    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.reports_path = os.path.join(self.base_path, 'reports')
        self.mailer_path = os.path.join(self.base_path, 'mailer')
        self.management_path = os.path.join(self.base_path, 'management')
        self.mailer_script = os.path.join(self.mailer_path, 'mailer.py')
        self.main_script = os.path.join(self.management_path, 'manager.py')
        self.system_config = os.path.join(self.base_path, 'intelmailer.conf')

        self.config = RawConfigParser(allow_no_value=True)
        self.config.read(self.system_config)

        self.log_path = self.config.get('log', 'path')
        self.logger = create_logger_main(self.log_path)
        
    def remove_report(self, report_id):
        self.reports[report_id].stop_report()
        del self.reports[report_id]
        
    def add_report(self, report_id, config_file, content_hash):
        try:
            state = ReportState(self.system_config, config_file, content_hash, self.log_path)
            self.reports[report_id] = state
        except:
            import traceback
            self.logger.error('There was an error adding report: %r' % config_file)
            self.logger.error(traceback.format_exc())
        
    def update_report(self, report_id, config_file, content_hash):
        try:
            self.remove_report(report_id)
            self.add_report(report_id, config_file, content_hash)
        except:
            import traceback
            self.logger.error('There was an error updating report: %r' % config_file)
            self.logger.error(traceback.format_exc())
        
    def reload_configs(self):
        self.logger.info('Reloading configurations')
        
        existent_reports = list()        
        for conffile in os.listdir(self.reports_path):
            if not conffile.endswith('.report'):
                continue

            fullpath_conffile = os.path.join(self.reports_path, conffile)
            report_id = get_report_filename_hash(fullpath_conffile)
            content_hash = get_report_contents_hash(fullpath_conffile)

            existent_reports.append(report_id)
            
            if report_id in self.reports:
                if self.reports[report_id].content_hash != content_hash:
                    self.logger.info('Modifying report: ' + fullpath_conffile)
                    self.update_report(report_id, fullpath_conffile, content_hash)
            else:
                self.logger.info('Adding new report: ' + fullpath_conffile)
                self.add_report(report_id, fullpath_conffile, content_hash)
            
        for report in self.reports.keys():
            if report not in existent_reports:
                self.logger.info('Removing report: ' + self.reports[report].config_file)
                self.remove_report(report_id)
                
    def start(self):
        self.reload_configs()
        self.timer = Timer(RELOAD_DELAY, self.start)
        self.timer.start()
        
    def join(self):
        self.timer.join()
        
    def stop(self):
        self.timer.cancel()
                
if __name__ == "__main__":
    daemon = ReportDaemon()
    daemon.start()
    daemon.join()
