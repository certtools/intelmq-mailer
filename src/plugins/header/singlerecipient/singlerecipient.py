# Local imports
from plugins.utils import pack_dictionary
from lib.plugins import HeaderPlugin

def initialize(report_config, log):
    return SingleRecipient(report_config, log)

class SingleRecipient(HeaderPlugin):
    def prepare_headers(self, email, report_config, dynamic_fields):
        email['Subject'] = report_config.get('singlerecipient', 'subject').decode('utf-8') % pack_dictionary(dynamic_fields, delimiter=',')
        email['From'] = report_config.get('singlerecipient', 'from').decode('utf-8')
        email['To'] = report_config.get('singlerecipient', 'to').decode('utf-8')
        email['Reply-to'] = report_config.get('singlerecipient', 'to').decode('utf-8')
