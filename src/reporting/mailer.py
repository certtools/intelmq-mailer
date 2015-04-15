# Insert path to make sure we can load the other modules
import os
import sys
base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, base_path)

# Global imports
import re
import importlib
from ConfigParser import RawConfigParser
from email.mime.multipart import MIMEMultipart
from datetime import timedelta, datetime

# Local imports
from lib.database import Database
from lib.logger import *
from lib.state import *

class Mailer():
    def __init__(self, report_config, state):
        self.report_config = state.config
        self.logger = state.logger
        self.state = state

        self.db = Database(self.state.config.get('database', 'host'), 
                           self.state.config.get('database', 'port'),
                           self.state.config.get('database', 'database'),
                           self.state.config.get('database', 'collection'))

        self.query_filter = self.get_filter()
        self.get_time_interval()

        self.date_field = self.state.config.get('general', 'date field')

        self.logger.info('Creating Mailer instance')

    def get_time_interval(self):
        self.fromdate = None
        self.todate = self.state.next_run
        
        if self.state.data_interval:
            self.fromdate = self.state.next_run - self.state.data_interval
        else:
            self.fromdate = self.state.previous_run

    def get_split_combinations(self):
        return self.db.get_distinct(self.report_config.options('split keys'), 
                                    datefield=self.date_field,
                                    dateinterval=(self.fromdate, self.todate), 
                                    refine=self.query_filter)

    def get_events(self, combination, filter_option=None):
        return self.db.get_events_from_combination(fields=self.report_config.options('event fields'), 
                                                   combination=combination, 
                                                   datefield=self.date_field,
                                                   dateinterval=(self.fromdate, self.todate), 
                                                   refine=self.query_filter)

    def get_filter(self):
        filter_dict = dict()
        
        if self.report_config.has_section('filter'):
            for (key, value) in self.report_config.items('filter'):
                filter_dict[key] = value

        return filter_dict

    def get_dynamic_fields(self, events):
        dynamic_fields = dict()
        # To add dynamic fields that aren't directly related to the data
        # do it like this:
        from datetime import date
        dynamic_fields['__today__'] = date.today().strftime("%d-%m-%Y")
        dynamic_fields['__count__'] = events.count()

        return dynamic_fields

    def check_combination_for_empty_fields(self, combination):
        for key in self.report_config.options('split keys'):
            if key not in combination:
                return True

            value = combination[key]
            if value is None or len(value) == 0:
                return True

        return False
    
    def prepare_plugins(self):
        header_plugins = self.report_config.get('plugins', 'headers').split(',')
        body_plugins = self.report_config.get('plugins', 'body').split(',')
        attachment_plugins = self.report_config.get('plugins', 'attachment').split(',')
        send_plugins = self.report_config.get('plugins', 'send').split(',')
        
        self.header_plugins = list()
        self.body_plugins = list()
        self.attachment_plugins = list()
        self.send_plugins = list()
        
        for plugin in header_plugins:
            try:
                plugin_name = plugin.strip()
                plugin_module = importlib.import_module('plugins.header.%s.%s' % (plugin_name, plugin_name))
                self.header_plugins.append(plugin_module.initialize(self.report_config, self.logger))
            except ImportError, e:
                import traceback
                self.logger.error(traceback.format_exc())
                '''Do nothing'''
                
        for plugin in body_plugins:
            try:
                plugin_name = plugin.strip()
                plugin_module = importlib.import_module('plugins.body.%s.%s' % (plugin_name, plugin_name))
                self.body_plugins.append(plugin_module.initialize(self.report_config, self.logger))
            except ImportError, e:
                import traceback
                self.logger.error(traceback.format_exc())
                '''Do nothing'''

        for plugin in attachment_plugins:
            try:
                plugin_name = plugin.strip()
                plugin_module = importlib.import_module('plugins.attachment.%s.%s' % (plugin_name, plugin_name))
                self.attachment_plugins.append(plugin_module.initialize(self.report_config, self.logger))
            except ImportError, e:
                import traceback
                self.logger.error(traceback.format_exc())
                '''Do nothing'''
                
        for plugin in send_plugins:
            try:
                plugin_name = plugin.strip()
                plugin_module = importlib.import_module('plugins.send.%s.%s' % (plugin_name, plugin_name))
                self.send_plugins.append(plugin_module.initialize(self.report_config, self.logger))
            except ImportError, e:
                import traceback
                self.logger.error(traceback.format_exc())
                '''Do nothing'''
        
    def call_header_plugins(self, email, dynamic_fields):
        for plugin in self.header_plugins:
            plugin.prepare_headers(email, self.report_config, dynamic_fields)

    def call_body_plugins(self, email, dynamic_fields, events):
        for plugin in self.body_plugins:
            plugin.prepare_body(email, self.report_config, dynamic_fields, events)

    def call_attachment_plugins(self, email, dynamic_fields, events):
        for plugin in self.attachment_plugins:
            plugin.prepare_attachments(email, self.report_config, dynamic_fields, events)
            
    def call_send_plugins(self, email, dynamic_fields, events):
        self.logger.info('Sending email')
        for plugin in self.send_plugins:
            self.logger.info('Sending by: %r' % type(plugin))
            plugin.send_email(email, self.report_config, dynamic_fields, events)

    def report(self):
        self.logger.info('Starting report')

        # Meant to initiate every plugin
        self.prepare_plugins()

        for (combination, count) in self.get_split_combinations():
            self.logger.info('Combination %r' % combination)
            if self.check_combination_for_empty_fields(combination):
                continue

            # Get events for this combination of values
            events = self.get_events(combination)

            # Add dynamic fields for convenience (like today's date)
            # These dynamic fields are meant to add static fields
            # that can be used in an email template like the event count
            # or todays date
            dynamic_fields = self.get_dynamic_fields(events)
            dynamic_fields.update(combination)

            # Create email MIME that will be manipulated by the plugins
            email = MIMEMultipart()

            # Meant to call every plugin that should add/modify headers of the email (to, from, subject, etc)
            self.call_header_plugins(email, dynamic_fields)

            # Meant to call every plugin that should add/modify the body of the email
            self.call_body_plugins(email, dynamic_fields, events)

            # Meant to call every plugin that should add/modify attachments of the email
            self.call_attachment_plugins(email, dynamic_fields, events)

            # The mail is ready. Send it
            self.call_send_plugins(email, dynamic_fields, events)
        self.logger.info('Finished report')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print 'Usage: %s system_config_file report_config_file logs_path' % sys.argv[0]
        sys.exit(-1)

    state = ReportState(sys.argv[1], sys.argv[2], '0', sys.argv[3])
        
