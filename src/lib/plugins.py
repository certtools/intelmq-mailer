class AttachmentPlugin(object):
    def __init__(self, report_config, log):
        self.report_config = report_config
        self.log = log

    def prepare_attachments(email, report_config, dynamic_fields, events):
        pass
    
class BodyPlugin(object):
    def __init__(self, report_config, log):
        self.report_config = report_config
        self.log = log

    def prepare_body(email, report_config, dynamic_fields, events):
        pass
    
class HeaderPlugin(object):
    def __init__(self, report_config, log):
        self.report_config = report_config
        self.log = log

    def prepare_headers(email, report_config, dynamic_fields):
        pass
    
class SendPlugin(object):
    def __init__(self, report_config, log):
        self.report_config = report_config
        self.log = log

    def send_email(email, report_config, dynamic_fields, events):
        pass
