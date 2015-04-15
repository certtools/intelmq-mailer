# Global imports
from datetime import date
import requests
import re

# Local imports
from plugins.utils import pack_dictionary
from lib.plugins import SendPlugin
from rtobjects import *

def initialize(report_config, log):
    return RT(report_config, log)
    
# Plugin main class

class RT(SendPlugin):
    def __init__(self, report_config, log):
        self.report_config = report_config
        self.log = log
        self.username = report_config.get('rt', 'username')
        self.password = report_config.get('rt', 'password')
        self.base_url = report_config.get('rt', 'url')
        
        if report_config.has_option('rt', 'retries'):
            self.retries = report_config.get('rt', 'retries')
        else:
            self.retries = 3
            
        incident = Incident()
        incident.subject = report_config.get('general', 'name') + ' - ' + date.today().strftime("%d-%m-%Y") #TODO: Maybe put this more flexible
        self.incident_id = self.create_ticket(incident)
        
    def get_url(self, url, content=None, files=None):
        import time
        retry = 0
        toRet = ""
        while retry <= self.retries:
            try:
                toRet = self._get_url(url, content, files)
                break
            except Exception, e:
                self.log.error('RT Connection failed - %r' % e)
                retry += 1
                time.sleep(30)

        self.log.info('RT Return: %s' % toRet)
        return toRet

    def _get_url(self, url, content=None, files=None):
        headers = {"Accept": "text/plain"}
        rest = self.base_url
        user = self.username
        passwd = self.password
        
        if not rest or not user or not passwd:
            print ("Could contact RT, bad or missing args (host: %s user: %s or passwd)", rest, user)
            return u""

        uri = rest + url

        data = {'user': self.username, 'pass': self.password, 'content': dict_to_rest(content)}
        response = requests.post(uri, data=data, files=files)
        response_data = response.text
        return response_data
    
    def create_ticket(self, ticket):
        content = ticket.to_dict()

        content[u'Owner'] = self.username
        data = self.get_url('ticket/new', content)

        ticketno = re.findall("(\d+) created.", data, re.M)

        if len(ticketno) == 0:
            self.log.error('Could not find ticket id. Returned data was:\n%s' % data)
            return None
        else:
            ticket.id = ticketno[0]
            return ticket.id
        
    def link_tickets(self, member, memberof):
        link = 'ticket/' + str(member) + '/links'
        content = {u'id': str(member), u'MemberOf': 'fsck.com-rt://cert.pt/ticket/%s' % str(memberof)}
        return self.get_url(link, content)
            
    def send_correspondence(self, correspond):
        url = 'ticket/' + str(correspond.ticket_id) + '/comment'
        content = correspond.to_dict()
        attachs = correspond.get_attachments()

        return self.get_url(url, content, attachs)
        
    def send_email(self, email, report_config, dynamic_fields, events):
        packed_fields = pack_dictionary(dynamic_fields)
        email_payloads = email.get_payload()
        
        investigation = Investigation()
        investigation.subject = report_config.get('rt', 'investigation_subject') % packed_fields
        
        for (custom_field, key) in report_config.items('rt investigation'):
            investigation.extra[custom_field] = packed_fields[key]
            
        investigation_id = self.create_ticket(investigation)
        self.link_tickets(investigation_id, self.incident_id)
        correspond = Correspondence(investigation_id)
        self.log.info('Investigation ID: %r' % investigation_id)
        
        if report_config.has_option('rt', 'cc'):
            correspond.cc = report_config.get('rt', 'cc').split(',')
            
        if report_config.has_option('rt', 'bcc'):
            correspond.bcc = report_config.get('rt', 'bcc').split(',')
            
        for payload in email_payloads:
            if payload.get_filename('') == '':
                correspond.text += payload.get_payload(decode=True)
            else:
                correspond.attachments.append((payload.get_filename(''), payload.get_payload(decode=True), payload.get_content_type()))
            
        self.send_correspondence(correspond)
