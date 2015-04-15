# To use this module it is required that one of the split keys has an entity id that can be queried in the whois.
# That key is passed in the 'id' option of the 'whois' section of the configs

# Global imports
import socket
import json

# Local imports
from plugins.utils import pack_dictionary
from plugins.utils import is_iterable
from lib.plugins import HeaderPlugin

def connect_to_whois(query_type, query):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('whois.rede.cert.pt', 43))
    s.send("-T %s %s" % (query_type, query))
    
    data = ''
    try:
        while True:
            local_data = s.recv(1024)
            if len(local_data) == 0:
                break
            else:
                data += local_data
    except:
        pass
        
    try:
        return json.loads(data)
    except:
        return data
    
def initialize(report_config, log):
    return Whois(report_config, log)

class Whois(HeaderPlugin):
    def prepare_headers(self, email, report_config, dynamic_fields):
        del email['To']
        
        id_key = report_config.get('whois', 'id')

        query_id = ''
        if is_iterable(dynamic_fields[id_key]):
            query_id = ''.join(dynamic_fields[id_key])
        else:
            query_id = unicode(dynamic_fields[id_key])

        email_contacts = connect_to_whois('abuse', 'ID:' + query_id)

        email['To'] = email_contacts
