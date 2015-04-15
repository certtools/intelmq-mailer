# Global imports
from email.mime.application import MIMEApplication
from StringIO import StringIO

import zipfile
import json
import csv

# Local imports
from plugins.utils import pack_dictionary
from lib.plugins import AttachmentPlugin

def initialize(report_config, log):
    return CSVAttach(report_config, log)

class CSVAttach(AttachmentPlugin):
    def prepare_attachments(self, email, report_config, dynamic_fields, events):
        # CSV configs
        csv_filename = report_config.get('attachcsv', 'filename').strip() % dynamic_fields
        zipcsv = report_config.has_option('attachcsv', 'zip')

        unziped_csv = StringIO()
        csvwriter = csv.DictWriter(unziped_csv, report_config.options('event fields'), delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writeheader()

        for event in events:
            csvwriter.writerow(pack_dictionary(event))
        
        final_csv = StringIO()
        final_csv_filename = ''

        if zipcsv:
            zip_data = StringIO()

            zfile = zipfile.ZipFile(zip_data, mode='w', compression=zipfile.ZIP_DEFLATED)
            zfile.writestr(csv_filename, unziped_csv.getvalue())
            zfile.close()

            final_csv = zip_data.getvalue()
            final_csv_filename = csv_filename + '.zip'
        else:
            final_csv = unziped_csv.getvalue()
            final_csv_filename = csv_filename

        part = MIMEApplication(final_csv)
        part.add_header('Content-Disposition', 'attachment', filename=final_csv_filename)
        email.attach(part)
