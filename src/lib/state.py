from threading import Timer
from datetime import datetime, timedelta
from ConfigParser import RawConfigParser

from reporting.mailer import Mailer
from lib.logger import *

class InvalidReportException(Exception):
    pass

class ReportState(object):
    config_file = None
    config = None
    first_run = None
    previous_run = None
    next_run = None
    interval = None
    timer = None
    logger = None
    date_format = '%d-%m-%Y %H:%M:%S'
    
    def run_report(self):
        # TODO: DO STUFF TO SEND EMAIL
        mailer = Mailer(self.config_file, self)
        mailer.report()

        self.previous_run = self.next_run
        self.next_run = self.next_run + self.interval

        time_to_report = self.next_run - datetime.utcnow()
        self.timer = Timer(time_to_report.total_seconds(), self.run_report)
        self.timer.start()
        
    def stop_report(self):
        self.timer.cancel()
        
    def __init__(self, system_config_file, config_file, content_hash, logs_path):
        self.content_hash = content_hash

        # Load and save configs
        self.config_file = config_file
        self.config = RawConfigParser(allow_no_value=True)
        self.config.readfp(open(system_config_file, 'r'))
        self.config.read(config_file)
        
        # Prepare logging instance
        self.logger = create_logger_report(logs_path, config_file)

        # If defined load date format, if not use the default one
        if self.config.has_option('general', 'date format'):
            self.date_format = self.config.get('general', 'date format')
        
        # Parse date of first run
        self.first_run = datetime.strptime(self.config.get('general', 'start date'), self.date_format)
        # DEBUG
        #self.first_run = datetime.utcnow() + timedelta(seconds=5)
        
        # Parse interval between reports
        interval_regex = '((((?P<days>\d+):)?(?P<hours>\d+):)?(?P<minutes>\d+):)?(?P<seconds>\d+)'
        match = re.match(interval_regex, self.config.get('general', 'time interval'))
        if match is None:
            self.logger.critical('Time interval could not be parsed. Format is: days:hours:minutes:seconds')
            raise InvalidReportException()
        else:
            days = int(match.group('days')) if match.group('days') else 0
            hours = int(match.group('hours')) if match.group('hours') else 0
            minutes = int(match.group('minutes')) if match.group('minutes') else 0
            seconds = int(match.group('seconds')) if match.group('seconds') else 0

            self.interval = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
            
        # Parse included data interval
        if self.config.has_option('general', 'report data interval'):
            match = re.match(interval_regex, self.config.get('general', 'report data interval'))
            if match is None:
                self.logger.critical('Report data interval could not be parsed. Format is: days:hours:minutes:seconds')
                self.data_interval = None
            else:
                days = int(match.group('days')) if match.group('days') else 0
                hours = int(match.group('hours')) if match.group('hours') else 0
                minutes = int(match.group('minutes')) if match.group('minutes') else 0
                seconds = int(match.group('seconds')) if match.group('seconds') else 0

                self.data_interval = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        else:
            self.data_interval = None
            
        # Calculate next run
        self.next_run = self.first_run
        
        # Calculate previous_run
        self.previous_run = self.first_run - self.interval

        # Create trigger for reporting
        time_to_report = self.first_run - datetime.utcnow()
        self.timer = Timer(time_to_report.total_seconds(), self.run_report)
        self.timer.start()

