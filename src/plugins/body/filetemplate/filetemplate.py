#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Global imports
from email.mime.text import MIMEText

# Local imports
from plugins.utils import pack_dictionary
from lib.plugins import BodyPlugin

def initialize(report_config, log):
    return FileTemplate(report_config, log)

class FileTemplate(BodyPlugin):
    def prepare_body(self, email, report_config, dynamic_fields, events):
        filename = report_config.get('filetemplate', 'template')
        template = open(filename, 'r')
        part = MIMEText(template.read().decode('utf-8') % pack_dictionary(dynamic_fields, delimiter=','), 'plain', 'utf-8')

        email.attach(part)
