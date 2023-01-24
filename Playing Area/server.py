import socket
import threading
import ssl
import sys
from ssl import SSLContext

sys.path.insert(0, '../functions')
from keyGen import keyGen
from timer import countdown
from addvalDict import addValDict

PORT = 7500
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

open("../server.txt", "w").write(SERVER)



class Server:

    def __init__(self) -> None:
        self.context = self.createContext()
        self.socket = self.createSocket(PORT)
        self.server = SERVER
        self.addr = ADDR
        self.port = PORT
        self.portstr = "{PORT}"


        self.counter = 0 
        self.clientsDict = {}
        self.deckSignatures = {}


        #controllers
        self.caller = False
        self.citizen = False
        self.activeConn = 0

        self.open = True
        self.countdown = False
        self.timer = 1

        #global lists
        self.disqualificationList = []
        self.finalDisqualifications = []
        self.msg = ''
        self.msg2 = ''
        self.msg3 = ''
        self.msg4 = ''
        self.valid = ''
        self.deck = ''
        self.finalDeck = []
        self.disqualificationListDeck = []
        self.finalDisqualificationsDeck = []

        #outcomes
        self.callerOutcome = []
        self.outcomeSignature = b''
        self.outcomeDisq = []
        self.winMsg = ''

        self.clientsDict = {}
        self.cards = {}
        self.playerWinners = {}


    

    def createContext(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(
                                certfile="./serverCRT/certificate.pem", 
                                keyfile="./serverCRT/key.pem"
                                )
        return context

    def createSocket(self, port):
        socketbind = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketbind.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socketbind.setblocking(True)
        socketbind.bind(ADDR)
        socketbind.listen()    #max connections
        return socketbind


    def timerToClose(self):
        if self.countdown == True:
            self.timer = countdown(0,1)
        else: pass
        return self.timer



    def handle_client(self,conn,dataHandler):
        self.connection = self.context.wrap_socket(conn, server_side=True)
        self.counter = self.counter + 1
        self.activeConn = self.activeConn + 1
        while True:
            try:
                dataHandler(self.connection)

            finally:
                self.closeConnection()


    def closeConnection(self):
            self.connection.close()
            self.activeConn = self.activeConn - 1





    def startListening(self,dataHandler):
        while self.open == True:
                while True:
                    try:
                        newsocket, client_addr = self.socket.accept()
                        thread = threading.Thread(target=self.handle_client, args=(newsocket,dataHandler))
                        thread.start()
                        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


                    except Exception as e:
                        print('[ERROR] There was a problem connecting to the server: ', e)
                        exit()



