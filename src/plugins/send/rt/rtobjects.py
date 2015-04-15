# Helper Functions

def decode(string):
    return string.decode('utf8')

def decode_and_justify(string):
    return string.decode('utf8').replace('\n', '\r\n ')

def encode(string):
    return string.encode('utf8')

def dict_to_rest(dictionary):
    rest = ''
    for (key, value) in dictionary.items():
        rest += '%s: %s\n' % (key, decode_and_justify(value))

    return rest

# RT Objects

class Ticket():
    queue = u'General'
    
    def __init__(self):
        self.subject = ''
        self.text = ''
        self.extra = dict()

    def __str__(self):
        return self.id + ': ' + self.subject

    def to_dict(self):
        rest = dict()
        rest[u'id'] = 'ticket/new'
        rest[u'Queue'] = self.queue
        rest[u'Subject'] = self.subject
        rest[u'Text'] = self.text

        for (key,value) in self.extra.items():
            rest[u'CF.{%s}' % key] = value

        return rest
    
class Incident(Ticket):
    queue = u'Incidents'
    
class Investigation(Ticket):
    queue = u'Investigations'

class Correspondence():
    def __init__(self, ticket_id):
        self.attachments = list() # An attachment is a tuple with (filename, bytes_of_attachment, mime_type)
        self.cc = list()
        self.bcc = list()
        self.text = ''
        self.ticket_id = ticket_id
        
    def to_dict(self):
        rest = dict()
        rest[u'id'] = encode(self.ticket_id)
        rest[u'Action'] = encode('Correspond')
        rest[u'Text'] = self.text
        
        if len(self.cc) > 0:
            rest[u'Cc'] = encode(','.join(self.cc))
            
        if len(self.bcc) > 0:
            rest[u'Bcc'] = encode(','.join(self.bcc))
            
        if len(self.attachments) > 0:
            rest[u'Attachment'] = encode('\n '.join([attach_name for (attach_name, attach_content, attach_type) in self.attachments]))

        return rest
            
    def get_attachments(self):
        post_attachments = dict()
        i = 1
        for (attach_name, attach_content, attach_type) in self.attachments:
            post_attachments['attachment_%d' % i] = (attach_name, attach_content, attach_type)
            i += 1
        return post_attachments