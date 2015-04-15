# Global imports
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

# TODO: Support SMTP/SSL - acho que ja esta

# Local imports
from lib.plugins import SendPlugin

def initialize(report_config, log):
    return Email(report_config, log)

class Email(SendPlugin):
    def send_mail(self, email, report_config, dynamic_fields, events):
        print "============= SENDING EMAIL ================="
        print email.as_string()
        print "============= END SENDING EMAIL ================="

        smtp = SMTP(report_config.get('mail server', 'server'), report_config.get('mail server', 'port'))
        if report_config.has_option('mail server', 'ssl'):
            smtp.starttls()
        
        smtp.ehlo()
        if report_config.has_option('mail server', 'username'):
            smtp.login(report_config.get('mail server', 'username'), report_config.get('mail server', 'password'))

        #smtp.sendmail(email['From'], email['To'].split(','), email.as_string())

