import socket , ssl , os , sys
from cryptography import x509
from ssl import SSLContext

sys.path.insert(0, '../functions')
from keyGen import keyGen

PORT = 7500
SERVER = open("../server.txt", "r").read()
#SERVER = '172.28.112.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
PATH = os.path.abspath("callerCRT")


class Caller:

    def __init__(self):
        self.context = self.createContext()
        self.connection = self.createConnection()


    def createContext(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        return context

    def createConnection(self):
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection = self.context.wrap_socket(s, server_side=False)
        return connection

    def startConnection(self, handler):
        try:
            self.connection.connect(ADDR)
            handler(self.connection)
            self.connection.close()
            
        except BrokenPipeError:
            print('[CLOSING SERVER] Server is closing due to insuficient players')

        except Exception as e:
                print('[ERROR] There was a problem connecting to the server: ', e)
                exit()