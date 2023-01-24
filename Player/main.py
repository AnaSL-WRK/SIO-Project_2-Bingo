import sys, os, pickle, random, time,json
from sys import platform

sys.path.insert(0, '../functions')
from client import Client
from CC2 import CC
from msgHandle import sendMsg, recvMsg, sendKey, recvKey
from keyGen import keyGen, symKeyGen
from signature import signMsg , verifySignature
from random_username.generate import generate_username
from cardGen import cardGen, cardGenCHEAT
from addvalDict import getKeyDict
from deckHandle import EncryptnShuffle, decrypt, chainDecrypt
BUFFER_SIZE = 2056


def dataHandler(connection):
   
    while True:
        try:
            leave = False

            #has game started?
            accepting = connection.recv(BUFFER_SIZE).decode("utf-8")       #r1
            if accepting == 'False':
                print('[ENDING CONNECTION] A game has already started. Please wait for the next one to be able to connect.')
                break


            cc = CC()

            #Client keys
            reg_private_key, reg_public_key = keyGen()

            #Server Public Key
            sv_public_key = connection.recv(BUFFER_SIZE)                   #r2

            #CC Validation
            if cc.validation == False:
                val = False
            else: 
                if cc.validate_certificate_chain() == False:
                    val = False
                else:
                    val = True

            connection.send(str(val).encode("utf-8"))                     #s1
            if (val == False):  
                recvMsg(connection,sv_public_key)[0]                     #ro1
                break                                              #Connection not allowed


            #Registration
            print("[client.connected] Connection to server was successful")


            ccprivate_key = keyGen()[0]  #cc.private_key()
            keys_certificate =cc.get_certificate_data('CITIZEN AUTHENTICATION CERTIFICATE') #b'certificado', case it goes wrong

        
            connection.send(reg_public_key)                          #s2

            sendKey(connection,ccprivate_key,reg_private_key)        ##
            sendKey(connection,keys_certificate,reg_private_key)     ##
    
            type_of_player = "Citizen"
            sendMsg(connection, type_of_player,reg_private_key)      #s3   - type of player

            username = generate_username(1)[0]
            sendMsg(connection,username,reg_private_key)             #s4  - username

            registration_msg = recvMsg(connection,sv_public_key)[0]  #r3  - reg msg
            print(registration_msg)


            #Game starting
            print(recvMsg(connection, sv_public_key)[0])              #r4 -  Waiting for players
            callerCheck = recvMsg(connection, sv_public_key)[0]       #r1p  -  bool check caller

            if callerCheck == 'False':
                print(recvMsg(connection, sv_public_key)[0])          #r2p - waiting for caller

            
            print(recvMsg(connection, sv_public_key)[0])                  #r3p   waiting for caller to sign

            print(recvMsg(connection, sv_public_key)[0])                #r5   game starting
            #GAME

            if platform == "win32":
                os.system("CLS")
            else:
                os.system("clear")
        

        
            print(recvMsg(connection, sv_public_key)[0])                #r6 - rules 

            if random.randint(0, 100) <= 10:
                card = cardGenCHEAT()
                print("I'm cheating this game, going to change my card")
            else:
                card = cardGen()


            pickledCards = pickle.dumps(card, -1) #pickled card
            signatureCards = signMsg(reg_private_key,bytearray(card))

            sendKey(connection,pickledCards,reg_private_key)        #s5 - signed card
            sendKey(connection,signatureCards,reg_private_key)      #s6 -signature


            playerCards =  pickle.loads(recvKey(connection,sv_public_key)[0])                  #r7 - cards  

            playerProfiles =  pickle.loads(recvKey(connection,sv_public_key)[0])                  #r8 - profiles
    

            prefix = getKeyDict(playerProfiles,reg_public_key)[0]


            # Print all cards

            for key in playerCards:
                seq = key
                username = playerProfiles[key][0]
                pubkey = playerProfiles[key][1]
                pcard = playerCards[key][0]
                print(f'Username: {seq}-{username}\n')
                print(f'PubKey: {pubkey}\n')
                print(f'Cards:')
                for i in range(0,len(pcard),3):
                    print("{:<8} {:<8} {:<8}".format(pcard[i], pcard[i+1],pcard[i+2] ))
                print('\n\n')




            disqualifications = []
        
            ##CARD VALIDATION
            for key in playerCards:
                pubkey = playerProfiles[key][1]
                pcard = playerCards[key][0]
                signature = playerCards[key][1]
                validation = verifySignature(pubkey,bytearray(pcard),signature)
                if validation == False or len(pcard) != 12 or len(set(pcard)) != len(pcard):
                    if key != prefix:
                        disqualifications.append(key) #not admitting to cheat

            
            if len(disqualifications) == 0:
                disqualifications.append('-1')

            print(f'I think these players cheated on their cards: {disqualifications}')

            sendKey(connection,pickle.dumps(disqualifications, -1),reg_private_key)     #s7 - list of disq


            disq = pickle.loads(recvKey(connection,sv_public_key)[0])                   #r4p- agreed disqualification list
        
            msg = recvMsg(connection,sv_public_key)[0]                                   #r9 - broadcast disq
            print(msg)


            for num in disq:
                if str(prefix) in num:
                    print('[LEAVING SERVER] Connection ending due to rule-breaking')
                    leave = True
                    break
            if leave == True:
                break
                    
            
                    

            print(f'\n\n')
            print(recvMsg(connection,sv_public_key)[0])                             #r10- rules 2

            #DECK HANDLE:
            symKey = symKeyGen()


            deck = pickle.loads(recvKey(connection,sv_public_key)[0])                #r5p- received deck
            newDeck = EncryptnShuffle(symKey,deck)
           

            sendKey(connection,pickle.dumps(newDeck,-1),reg_private_key)             #s8- deck
            sendKey(connection,symKey,reg_private_key)                               #s9 - key


            if random.randint(0, 100) <= 10:
                cheatingKey = keyGen()[0]
                print("I'm cheating this game by tampering with the deck")
                signature = signMsg(cheatingKey,b''.join(newDeck))
            else:
                signature = signMsg(reg_private_key,b''.join(newDeck))

            sendKey(connection,signature,reg_private_key)                            #s10 - signature


            

            deckDict = pickle.loads(recvKey(connection,sv_public_key)[0])           #r12 - dict

            #verifying if its the right final deck
            lastKey = list(deckDict)[-1]
            commitedDeck = deckDict[lastKey][0]
            caller = list(deckDict)[0]
            callerSignature = deckDict[caller][3] 
            callerPubKey = playerProfiles[caller][1] 


            boolSign = verifySignature(callerPubKey,b''.join(commitedDeck),callerSignature)
            
            sendMsg(connection,str(boolSign),reg_private_key)                       #s1p - did caller cheat

            #if caller tampered with the commited deck, player can abandon game
            if boolSign == False:            
                print(recvMsg(connection,sv_public_key)[0])                        #r5p - you can leave game
                if random.randint(0, 100) <= 50:
                    break

            #deckDict = {seq: [deck he encripted, symkey, signature]}
            arrSymKeys = []
            disqualifications.clear()

            # validating decryptions
            for i in range(len(deckDict)-1,-1,-1):
                key = str(list(deckDict)[i])
                seq = key
                username = playerProfiles[key][0]
                pubkey = playerProfiles[key][1]
                skey = deckDict[key][1]
                deck = deckDict[key][0]
                signature = deckDict[key][2]

                arrSymKeys.append(skey)
                print(f'Username: {seq}-{username}\n')
                print(f'PubKey: {pubkey}\n')
                print(f'Encrypting Key: {skey}\n')
                print(f'Encripted Deck: {deck}\n\n')
                
                validation = verifySignature(pubkey,b''.join(deck),signature)
                if key == 0:
                    boolFirstDeck = validation
                else: 
                    if validation == False:
                        if key != prefix:       #not admiting to cheat
                            disqualifications.append(key)
                print('\n\n')


                decryptedDeck = decrypt(skey,deck)

                compare = []
                if i != 0 :
                    for j in decryptedDeck:
                        if j not in deckDict[str(list(deckDict)[i-1])][0]:
                            compare.append('False')
                        else:
                            compare.append('True')
                    if list(compare) == 'False':
                        if key != prefix:       #not admiting to cheat
                            disqualifications.append(key)


            if len(disqualifications) == 0:
                disqualifications.append('-1')

        
            print(f'I think these players cheated when making the deck: {disqualifications}')
            
            sendKey(connection,pickle.dumps(disqualifications, -1),reg_private_key)     #s11 disqualifications from deck val

            print(recvMsg(connection,sv_public_key)[0])                                  #r13 - broadcast disq 
    

            disqDeck = pickle.loads(recvKey(connection,sv_public_key)[0])           #r6p- agreed disqualification list
                
            if str(prefix) in disqDeck:
                print('[LEAVING SERVER] Connection ending due to rule-breaking')
                break

            for d in disqDeck:
                if '-1' in d:
                    disqDeck.remove(d)

            if len(disqDeck)>=1:
                print('[LEAVING SERVER] Connection ending due compromise of integrity of the game')
                break


            #getting deck:
            finalDeck = chainDecrypt(arrSymKeys,commitedDeck,0)
            sendKey(connection,pickle.dumps(finalDeck, -1),reg_private_key)             #s12 final deck

            if len(finalDeck)>48:
                print('The caller was found producing an invalid deck. You may leave the game if you wish')
                if random.randint(0, 100) <= 40:
                    break   



            valid = recvMsg(connection,sv_public_key)[0]                            #r7c
            msg = recvMsg(connection,sv_public_key)[0]                              #r8c                                                                   
            print(msg)

            if valid == 'Invalid':
                break



            #getting winners:

            print(f'\nYour card:')
            for i in range(0,len(card),3):
                print("{:<8} {:<8} {:<8}".format(card[i], card[i+1],card[i+2]))

            print('\n\n')

            print(f'Lobby:')
            for key in playerCards:
                if key != str(prefix):
                    seq = key
                    username = playerProfiles[key][0]
                    pcard = playerCards[key][0]
                    print(f'Username: {seq}-{username}\n')
                    print(f'Cards:')
                    for i in range(0,len(pcard),3):
                        print("{:<8} {:<8} {:<8}".format(pcard[i], pcard[i+1],pcard[i+2] ))
                    print('\n\n')


            
            winners = {}
            #winners = {seq: index of deck where card finished}

            for key in playerCards:
                seq = key
                username = playerProfiles[key][0]
                card = playerCards[key][0]
                numbersHere = {}

                for i in range(len(finalDeck)):
                    if finalDeck[i] in card:
                        numbersHere[i] = 'True'
                    else:
                        pass
                
                if len(numbersHere) == len(card):
                    lastNum = list(numbersHere)[-1]
                    winners[str(seq)] = lastNum+1
                else:
                    winners[str(seq)] = '-1'
                
                numbersHere.clear()

    

            if winners.get(str(prefix)) == '-1':
                if random.randint(0, 100) <= 10:
                    print("I didn't win. I'll have to cheat when calling my outcome.")
                    winners[str(prefix)] = random.randint(0, 49)
                else:
                    print("I didn't win")
            else:
                print(winners.get(str(prefix)))

                print(f"I won at position {winners.get(str(prefix))}")

            
            outcomeSignature = signMsg(reg_private_key, json.dumps(winners).encode('utf-8'))

    

            sendKey(connection,pickle.dumps(winners, -1),reg_private_key)               #s13
            sendKey(connection,outcomeSignature,reg_private_key)                        #s14

            callerOutcome = pickle.loads(recvKey(connection, sv_public_key)[0])        #r7p
            callerOutcomeSignature = (recvKey(connection, sv_public_key)[0])           #r8p
                   
            msg = recvMsg(connection,sv_public_key)[0]                                 #r9p
            disqArr = pickle.loads(recvKey(connection, sv_public_key)[0])              #r10p

            if msg == 'Valid':
                pass
            else:
                print(msg)

  
            if str(prefix) in disqArr:
                print('[LEAVING SERVER] Connection ending due to rule-breaking')
                break

            
           


            winMsg = recvMsg(connection,sv_public_key)[0]                             #r11p

            if verifySignature(callerPubKey,winMsg.encode('utf-8'),callerOutcomeSignature) == False:
                            print('Game outcome message was found having an invalid signature from the caller. You may abandon the game if you wish')
                            if random.randint(0, 100) <= 40:
                                break   
   
            print(winMsg)

            time.sleep(3000)
            break



        except Exception as e:
            print(e)
            break




client = Client()
client.startConnection(dataHandler)