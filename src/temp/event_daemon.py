import SocketServer
import json

from lib.database import Database

EVENT_POOL_NAME = "events"

class EventHandler(SocketServer.StreamRequestHandler):
    def event_parsing(self, data):
        return json.loads(data)

    def handle(self):
        self.database = getattr(self, 'database', Database())

        # Read line from socket. Each line is an event.
        self.data = self.rfile.readline().strip()
        
        # Get event from data
        self.parsed = self.event_parsing(self.data)
        
        # Save event in database
        self.database.save_event(EVENT_POOL_NAME, self.parsed)

if __name__ == '__main__':
    HOST, PORT = 'localhost', 9999
    
    server = SocketServer.TCPServer((HOST, PORT), EventHandler)

    try:
        server.serve_forever()
    except:
        server.shutdown()

