import logging
import time
import sys
import pickle


sys.path.insert(0, '../functions')

from msgHandle import PAsendMsg, PArecvMsg, PAsendKey, PArecvKey, pickleLoad
from signature import signMsg
from addvalDict import addValDict
from keyGen import keyGen
from server import Server

logger = logging.getLogger()      

BUFFER_SIZE = 2056

def dataHandler(connection):

    while closeS == False:

        try:

            #Server keys
            sv_private_key, sv_public_key  = keyGen()

            #User list to hold username and pubkey
            userNpub = []

            #has game started?
            connection.send(str(server.open).encode("utf-8"))               #s1


            #Sending server_public_key for msg validation
            connection.send(sv_public_key)                                  #s2


            #Client cert validation
            validation = (connection.recv(BUFFER_SIZE)).decode("utf-8")      #r1
            if validation == "False":
                msg = ("[ENDING CONNECTION] Connection denied due to invalid Citizen Card information")
                PAsendMsg(connection,msg,sv_private_key)                     #s1o 
                break


            #Begin client registration
            
            print(f"[NEW CONNNECTION] {connection} connected.")
            
            
            registry_pub_key = connection.recv(BUFFER_SIZE)                 #r2

            cc_private_key = PArecvKey(connection,registry_pub_key,server)[0]                            ##
            cc_certificate = PArecvKey(connection, registry_pub_key,server)[0].decode('utf-8')           ##

            identity = PArecvMsg(connection,registry_pub_key,server)[0]     #r3  - type of player
                

            #Creating user profile
            if identity == 'Caller':
                prefix = 0
                server.counter = server.counter -1
                server.caller = True
            else:
                prefix = server.counter
                server.citizen = True

            username = PArecvMsg(connection,registry_pub_key,server)[0]        #r4 - username

        
            #User Created and signed
            msg = f"[REGISTRATION COMPLETE] Welcome to pyBingo {prefix}-{username}!"
            PAsendMsg(connection,msg,sv_private_key)                            #s3


            #Registration Message Signed and Saved
            t = time.localtime()
            current_time = time.strftime("%D - %H:%M:%S", t)
            reg = f"User {prefix}-{username} registered at {current_time}\nCertificate: {cc_certificate}\n"
            signed = signMsg(cc_private_key,reg.encode('utf-8'))
            open(f"./Registrations/registration-{prefix}{username}.txt", "a").write(reg + f"Signature: {signed}\n")



        
            msg = f"[WAITING] Now waiting for players to join the playing area. \n[MAXIMUM WAIT TIME]: 2 minutes"
            PAsendMsg(connection,msg,sv_private_key)                            #s4



            if server.countdown == False:
                server.countdown = True
                server.timerToClose()

            while server.timer != 0:
                time.sleep(1)

            if identity == 'Citizen':
                PAsendMsg(connection,str(server.caller),sv_private_key)        #s1p
                if server.timer == 0 and server.caller == False :
                    PAsendMsg(connection,"[WAITING...] Waiting for caller to respond",sv_private_key)    #s2p
            


            while (server.caller == False or server.citizen == False):
                time.sleep(1)

            
            server.open = False

        
            #Updating user dictionary (prefix: [username, key]). Commited user list
            userNpub.append(username)
            userNpub.append(registry_pub_key)
            addValDict(server.clientsDict,str(prefix),userNpub)


            while len(server.clientsDict) != server.activeConn:
                time.sleep(0.1)

            #Sending citizen profiles for caller to sign
            if identity == "Citizen":
                PAsendMsg(connection,'[WAITING FOR CALLER] Caller is now signing your player profile', sv_private_key)  #s3p
            else: 
                print(f'\n\nUsers: {server.clientsDict}\n')
                PAsendMsg(connection,str(len(server.clientsDict)),sv_private_key)                               #s1c
                for key in server.clientsDict:
                    PAsendMsg(connection,str(key),sv_private_key)                                               #s2c - seq                    
                    PAsendMsg(connection,server.clientsDict[key][0],sv_private_key)                            #s3c - username       
                    PAsendKey(connection,server.clientsDict[key][1],sv_private_key)                             #s4c - key     



            user_list = dict(server.clientsDict)

            PAsendMsg(connection,"[GAME STARTING] pyBingo may now begin!",sv_private_key)     #s5

            

            #GAME
            rules = """Welcome to pyBingo!\n\nRules of the game:\npyBingo is played with a deck of numbers from 0-46.
                    \nAt the beginning of the game each player will choose, or generate, their own card of 12 numbers.\nAfter all cards are sent to the playing area and validated by each participant, the game will begin!
                    \nTo ensure that the game is fair, a random deck is firstly created by the caller, signed and encrypted by him.\nThen that same deck will pass from player to player (following order of registration), getting shuffled, encrypted and \nsigned by each player it passes through. At the end, the deck returns to the caller and is posted back to the Playing area.
                    \nAll players should then decrypt the deck by following the reverse order encryption and arrive at a final deck everyone agrees.
                    \n\nTo check if you win you must follow the commited order of numbers from the deck (line by line), crossing the numbers you own.
                    \nSince all player cards are commited to the playing Area at the beggining of the game, you can check your peer's cards as well!\nAt the end, everyone should agree on the same winner(s).
                    \n\nAny violation of the game's rules such as:    
                    \n- Generation of invalid card or deck (containing repeated numbers, invalid size, incorrect signature)
                    \n- Falsely communicating outcome
                    \n- Communicating using invalid messages (incorrect signature)
                    \nWill be ground for disqualification, broadcasted to all.
                    \n\nGood luck and have fun!\n\n"""
                                            
            PAsendMsg(connection,rules,sv_private_key)                                           #s6



            if identity == 'Citizen':
                playerCardPickle = PArecvKey(connection,registry_pub_key,server)[0]        #r5  -players card
                cardSignature =  PArecvKey(connection,registry_pub_key,server)[0]       #r6  -players card signature
                playerCard =  pickleLoad(playerCardPickle)
                addValDict(server.cards,str(prefix),[playerCard,cardSignature])
                if playerCard == None:
                    playerCard = ['-1']

            while len(server.cards) != server.activeConn-1:
                time.sleep(1)


            server.cards = dict(sorted(server.cards.items()))
            playercardsdict = pickle.dumps(server.cards, -1)
            PAsendKey(connection,playercardsdict,sv_private_key)             #s7 - players cards
            
            server.clientsDict = dict(sorted(server.clientsDict.items()))
            playerprofiledict = pickle.dumps(server.clientsDict, -1)        #s8 - players profiles
            PAsendKey(connection,playerprofiledict,sv_private_key)


    
            disqualifications = pickleLoad(PArecvKey(connection,registry_pub_key,server)[0])   #r7 - disqualifications
            if disqualifications == []:
                disqualifications = ['-1']
            server.disqualificationList.append(disqualifications)

     

            while(len(server.disqualificationList)<server.activeConn):
                time.sleep(1)


            if identity== 'Caller':
                PAsendKey(connection,pickle.dumps(server.disqualificationList, -1),sv_private_key)    #s5c -disq list (arr of arr)
                server.finalDisqualifications = pickleLoad(PArecvKey(connection,registry_pub_key,server)[0])  #r1c (agreed disq arr)
                server.msg = PArecvMsg(connection, registry_pub_key, server)[0]             #r2c - disq msgs

                print(f'Disqualified users: {server.disqualificationList}\n')
            while server.msg == '':
                time.sleep(1)


            if identity == 'Citizen':
                    PAsendKey(connection,pickle.dumps(server.disqualificationList, -1),sv_private_key)  #s4p


            PAsendMsg(connection,server.msg,sv_private_key)                       #s9 - disqualification broadcast
            
            for arr in server.disqualificationList:
                    for num in arr:
                        if num in server.clientsDict:
                            del server.clientsDict[str(num)]
                            break
            time.sleep(5)

            if len(server.clientsDict) == 1:
                print('[CLOSING SERVER] Server is closing due to insuficient players')
                break

            #send instructions for decryption

            intructions = f"""Please ensure that you encrypt and shuffle the encrypted deck you receive,signing it before commiting to the Playing Area. 
                        \nFor the chain decryption and validation of the deck, please use the inverse order of registration and confirm the signature (with the respective public key) and decrypt the block with the respective users symmetric key.
                        \nEveryone should arrive at the same final deck, and any dishonest player will be disqualified.
                        \nPlayers can choose to abandon the game if:
                        \n- The caller was found tampering with the final encrypted deck (wrong final signature) 
                        \n- The agreed final deck is invalid (wrong size, signature or numbers)\n\n"""

            PAsendMsg(connection,intructions,sv_private_key)                                    #s10- rules2

            time.sleep(5)

            #adicionar dict a seq e signa
            temp = []
            if identity == 'Caller':
                deck =  pickleLoad(PArecvKey(connection,registry_pub_key,server)[0])  #r8 caller initial deck
                symkey = PArecvKey(connection,registry_pub_key,server)[0]                      #r9 key
                signature = PArecvKey(connection,registry_pub_key,server)[0]                #r10 signatures
                temp.append(deck)
                temp.append(symkey)
                temp.append(signature)
                addValDict(server.deckSignatures,str(prefix),temp)
                temp.clear()


    
  
            while len(server.deckSignatures) == 0:
                time.sleep(1)

      
            
            
            if identity == 'Citizen':
                for i in server.clientsDict:
                    if str(prefix) == i:             
                        temp.clear()
                        lastKey =  list(server.deckSignatures)[-1]
                        lastCommitedDeck = server.deckSignatures[lastKey][0]
                        PAsendKey(connection,pickle.dumps(lastCommitedDeck,-1),sv_private_key)               #s5p temp decks
                        tempDeck =  pickleLoad(PArecvKey(connection,registry_pub_key,server)[0])   #r8 rotating deck
                        if tempDeck == []:
                            continue
                        else:
                            deck = tempDeck
                        symkey = PArecvKey(connection,registry_pub_key,server)[0]                       #r9 key
                        signature = PArecvKey(connection,registry_pub_key,server)[0]                    #r10 signatures
                        temp.append(deck)
                        temp.append(symkey)
                        temp.append(signature)
                        addValDict(server.deckSignatures,str(prefix),temp)

                    else: 
                        while (str(i) in server.deckSignatures) == False:

                            time.sleep(3)

        
            while len(server.deckSignatures) != len(server.clientsDict):
                time.sleep(3)

            if identity == 'Caller':
                temp = []
                lastKey =  list(server.deckSignatures)[-1]
                lastCommitedDeck = server.deckSignatures[lastKey][0]
                PAsendKey(connection,pickle.dumps(lastCommitedDeck,-1),sv_private_key)                  #s6c final deck for caller to sign
                signature = PArecvKey(connection,registry_pub_key,server)[0]                   #r3c signature
                temp.append(signature)
                addValDict(server.deckSignatures,str(prefix),temp)

            while len(server.deckSignatures['0'])!=4:
                time.sleep(1)

            #decks dictionary = {seq: [deck seq encripted, symkey, signature]})

            PAsendKey(connection,pickle.dumps(server.deckSignatures, -1),sv_private_key)    #s12 sending dict




            if identity == 'Citizen':
                #was the commited deck the right one or did caller cheat?
                gameDeck = PArecvMsg(connection,registry_pub_key,server)[0]             #r1p

                if gameDeck == 'False':
                    PAsendMsg(connection,'The Caller was detected cheating (tampering with commited deck). You may abandon the game if you wish.\n',sv_private_key)   #s5p





            ### disqualifications from deck validation 


            disqualifications = pickleLoad(PArecvKey(connection,registry_pub_key,server)[0])   #r11 - disqualifications
            if disqualifications == []:
                disqualifications = ['-1']


            server.disqualificationListDeck.append(disqualifications)

            while(len(server.disqualificationListDeck) < len(server.clientsDict)):
                time.sleep(1)


            if identity== 'Caller':
                PAsendKey(connection,pickle.dumps(server.disqualificationListDeck, -1),sv_private_key)    #s7c -disq list (arr of arr)
                server.finalDisqualificationsDeck =pickleLoad(PArecvKey(connection,registry_pub_key,server)[0])#r4c (agreed disq arr)
                server.msg2 = PArecvMsg(connection, registry_pub_key, server)[0]             #r5c - disq msgs
            else:
                while server.msg2 == '':
                    time.sleep(1)


            if server.finalDisqualificationsDeck== [] or len(server.finalDisqualificationsDeck) == 0:
                server.finalDisqualificationsDeck = ['-1']

                

            PAsendMsg(connection,server.msg2,sv_private_key)                       #s13 - disqualification broadcast

            if identity == 'Citizen':
                PAsendKey(connection,pickle.dumps(server.finalDisqualificationsDeck,-1),sv_private_key)  #s6p - disq list
                
            time.sleep(3)
            #did everyone arrive at the same deck?
            decks = pickleLoad(PArecvKey(connection,registry_pub_key,server)[0])   #r12 - decks
            server.finalDeck.append(decks)


            for arr in server.finalDisqualificationsDeck:
                if arr in server.clientsDict:
                    del server.clientsDict[str(arr)]
                    break

            if len(server.clientsDict) == 1:
                time.sleep(5)
                print('[CLOSING SERVER] Server is closing due to insuficient players')
                break


            while (len(server.finalDeck) < len(server.clientsDict)):
                time.sleep(1)

            
            if identity == 'Caller':
                    PAsendKey(connection,pickle.dumps(server.finalDeck, -1),sv_private_key)  #s8c
                    server.valid = PArecvMsg(connection,registry_pub_key,server)[0]            #r6c - game validation
                    server.msg3 = PArecvMsg(connection, registry_pub_key, server)[0]             #r7c  - msg
            else:
                while server.msg3 == '':
                    time.sleep(3)


            
##################
            if identity == 'Citizen':
                temp = []
                PAsendMsg(connection,server.valid,sv_private_key)  #s7p
                PAsendMsg(connection,server.msg3,sv_private_key)  #s8p
                playerOutcome = pickleLoad(PArecvKey(connection,registry_pub_key,server)[0])     #r13    each player computes all winners
                outcomeSignature = PArecvKey(connection,registry_pub_key,server)[0]                #r14    signature
                temp.append(playerOutcome)
                temp.append(outcomeSignature)
                addValDict(server.playerWinners,str(prefix),temp)
                #server player winners = {seq: their outcome of the game (results from everyone),signature}


            while(len(server.playerWinners)) == 0:
                time.sleep(1)

            time.sleep(5)



            if identity == 'Caller':
                server.callerOutcome = pickleLoad(PArecvKey(connection,registry_pub_key,server)[0])                    #r13    - caller outcome - pickle
                PAsendKey(connection,pickle.dumps(server.playerWinners, -1),sv_private_key)         #s9c  - players win dict

                server.outcomeDisq = pickleLoad(PArecvKey(connection, registry_pub_key,server)[0])                     #r8c - disq arr - pickle
                server.msg4 = PArecvMsg(connection, registry_pub_key,server)[0]                     #r9c - disq msgs
                server.winMsg =  PArecvMsg(connection, registry_pub_key,server)[0]                         #r10c - winners msg
                server.outcomeSignature = PArecvKey(connection,registry_pub_key,server)[0]                #r14    - caller outcome signature
                print(f'Final Deck: {server.finalDeck}\n\n')
                print(f'Winners!: {server.callerOutcome}\n')

            while server.msg4 == '':
                time.sleep(1)
                while server.callerOutcome == []:
                    time.sleep(1)
                    while server.outcomeSignature == b'':
                        time.sleep(1)
                        while server.outcomeDisq == []:
                            time.sleep(1)
                            while server.winMsg == '':
                                time.sleep(1)
                                


            

            if identity == 'Citizen':
                PAsendKey(connection,pickle.dumps(server.callerOutcome,-1),sv_private_key)  #s7p
                PAsendKey(connection,server.outcomeSignature,sv_private_key)                #s8p
                PAsendMsg(connection,server.msg4,sv_private_key)                            #s9p
                PAsendKey(connection, pickle.dumps(server.outcomeDisq,-1),sv_private_key)   #s10p
                
                time.sleep(3)

                PAsendMsg(connection,server.winMsg,sv_private_key)                          #s11p


            pp = open('player_profiles.txt', 'w+')
            for key in user_list:
                seq = key
                username = user_list[key][0]
                pubkey = user_list[key][1]
                pp.write(f'Username: {seq}-{username}\n')
                pp.write(f'PubKey: {pubkey}\n\n')
            pp.close()
        
            time.sleep(3000)
        
        except Exception as e:
            time.sleep(5)
            break



           
print("[STARTING] Server is starting...")
server = Server()
print("[LISTENING] Server is listening")
closeS = False
server.startListening(dataHandler) 

