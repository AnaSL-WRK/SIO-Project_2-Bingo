import sys,pickle
from signature import signMsg, verifySignature
from addvalDict import getKeyDict
from logger import log, HashgetLastLine
from cryptography.hazmat.primitives import hashes

sys.path.insert(1, '../Playing Area')
from server import Server

BUFFER_SIZE = 8000



def sendMsg(connection, data, privkey):
    
    
    encoded = data.encode("utf-8")
    signature = signMsg(privkey,encoded)
    connection.send(signature)
    connection.send(encoded)


def recvMsg(connection,pubkey):
    signature = connection.recv(BUFFER_SIZE)
    data = connection.recv(BUFFER_SIZE)
    decoded = data.decode("utf-8")
    valid = verifySignature(pubkey,data,signature)
 
    return decoded, valid


def sendKey(connection, key, privkey):
    signature = signMsg(privkey,key)
    connection.send(signature)
    connection.send(key)


def recvKey(connection,pubkey):
    signature = connection.recv(BUFFER_SIZE)
    key = connection.recv(BUFFER_SIZE)
    valid = verifySignature(pubkey,key,signature)

    return key, valid  


#   Playing Area  - includes logging


def PAsendMsg(connection, data, privkey):
    

    seq = "PA"
    prevEntry = HashgetLastLine()

    encoded = data.encode("utf-8")
    signature = signMsg(privkey,encoded)
    try:
        connection.send(signature)
        connection.send(encoded)

        extra = {'seq': seq, 'hash':prevEntry, 'signature':signature}
        log(extra,data)
    except:
        pass

def PArecvMsg(connection,pubkey,server):
    
    lst = server.clientsDict

    seq =   str(getKeyDict(lst,pubkey))
    prevEntry = HashgetLastLine()

    signature = connection.recv(BUFFER_SIZE)
    data = connection.recv(BUFFER_SIZE)

    if not data or not signature:
        closeS = True
        return

    decoded = data.decode("utf-8")
    valid = verifySignature(pubkey,data,signature)

    extra = {'seq': seq, 'hash':prevEntry, 'signature':signature}
    log(extra,decoded)

    return decoded, valid




def PAsendKey(connection, key, privkey):
    seq = "PA"
    prevEntry = HashgetLastLine()

    signature = signMsg(privkey,key)
    try:
        connection.send(signature)
        connection.send(key)

        extra = {'seq': seq, 'hash':prevEntry, 'signature':signature}
        log(extra,key)
    except:
        pass

def PArecvKey(connection,pubkey,server):

    lst = server.clientsDict
    seq =   str(getKeyDict(lst,pubkey))
    prevEntry = HashgetLastLine()

    signature = connection.recv(BUFFER_SIZE)
    key = connection.recv(BUFFER_SIZE)

    if not key or not signature:
        closeS = True
        return
    valid = verifySignature(pubkey,key,signature)
 
    extra = {'seq': seq, 'hash':prevEntry,'signature':signature}
    log(extra,key)

    return key, valid  

def pickleLoad(data):    
    try:
        return(pickle.loads(data)) 
    except:
        empty = []
        return empty

    