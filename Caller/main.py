import sys,os, pickle, random, time,json
from caller import Caller
from sys import platform
from collections import Counter


sys.path.insert(0, '../functions')

from msgHandle import sendMsg, recvMsg, sendKey, recvKey
from CC2 import CC
from keyGen import keyGen, symKeyGen
from signature import signMsg, verifySignature
from addvalDict import addValDict
from cardGen import deckGen, deckGenCHEAT
from deckHandle import CallerEncryptnShuffle, decrypt, chainDecrypt
from random_username.generate import generate_username

BUFFER_SIZE = 1024

def dataHandler(connection):
   
    while True:

        try:
            cc = CC()

            #Caller keys
            reg_private_key, reg_public_key = keyGen()
    

            #Dictionary with signed profiles 
            signed_users = {}           #seq, username/signed username, key/signed key


            #has game started?
            accepting = connection.recv(BUFFER_SIZE).decode("utf-8")                    #r1

            #Server Public Key
            sv_public_key = connection.recv(BUFFER_SIZE)                                #r2
            

            #CC Validation
            if cc.validation == False:
                val = False
            else: 
                if cc.validate_certificate_chain() == False:
                    val = False
                else:
                    val = True



            #print(val)
            connection.send((str(val)).encode("utf-8"))                              #s1
            if (val == False):
                recvMsg(connection,sv_public_key)[0]                                #r1o
                break                                                               #Connection not allowed


            #Registration
            print("[CONNECTED] Connection to server was successful")

            ccprivate_key = keyGen()[0] #cc.private_key() ##CHALLENGE RESPONSE
            keys_certificate =cc.get_certificate_data('CITIZEN AUTHENTICATION CERTIFICATE') # b'certificado', case it goes wrong

            connection.send(reg_public_key)                                         #s2

            sendKey(connection,ccprivate_key,reg_private_key)                       ##
            sendKey(connection,keys_certificate,reg_private_key)                    ##
            
            type_of_player = 'Caller'
            sendMsg(connection, type_of_player,reg_private_key)                     #s3 - type of player      
            

            username = generate_username(1)[0]
            sendMsg(connection,username,reg_private_key)                            #s4 - username
                

            #User Created and signed
            print(recvMsg(connection,sv_public_key)[0])                             #r3 - reg msg

            
        
            #Game starting
            print(recvMsg(connection,sv_public_key)[0])                             #r4 -waiting players
            


            #Signing citizens profiles
            dictlen = int((recvMsg(connection,sv_public_key)[0]))                   #r1c - total number, dictlen-1= n players



            for i in range(dictlen):
                print('Signing players profiles...')
                lst = []
                prefix = (recvMsg(connection,sv_public_key)[0])                     #r2c  -seq
                
                username = recvMsg(connection,sv_public_key)[0]                     #r3c  -username
                try:
                    signU = signMsg(reg_private_key,username.encode('utf-8'))
                except: pass
                lst.append(username)
                lst.append(signU)
                
        
                key = recvKey(connection,sv_public_key)[0]                          #r4c  -key
                signK = signMsg(reg_private_key,key)
                lst.append(key)
                lst.append(signK)
        
                addValDict(signed_users,prefix,lst)
                lst.clear()


            print(recvMsg(connection,sv_public_key)[0])                             #r5 - starting 

            #GAME START
            if platform == "win32":
                os.system("CLS")
            else:
                os.system("clear")
        
            print(recvMsg(connection, sv_public_key)[0])                        #r6 - rules


            pickledDict = recvKey(connection,sv_public_key)[0]                  #r7 - cards
            playerCards = pickle.loads(pickledDict) #data loaded.

            
            pickledDictprofile = recvKey(connection,sv_public_key)[0]                  #r8 - profiles
            playerProfiles = pickle.loads(pickledDictprofile) #data loaded.


            #CARD PRINTING
            for key in playerCards:
                seq = key
                username = playerProfiles[key][0]
                pubkey = playerProfiles[key][1]
                card = playerCards[key][0]
                print(f'Username: {seq}-{username}\n')
                print(f'PubKey: {pubkey}\n')
                print(f'Cards:')
                for i in range(0,len(card),3):
                    print("{:<8} {:<8} {:<8}".format(card[i], card[i+1],card[i+2] ))
                print('\n\n')

            
            
            ##CARD VALIDATION
            clean = []
            disqualifications = []
            for key in playerCards:
                pubkey = playerProfiles[key][1]
                card = playerCards[key][0]
                signature = playerCards[key][1]
                validation = verifySignature(pubkey,bytearray(card),signature)
                if validation == False or len(card) != 12 or len(set(card)) != len(card):
                    disqualifications.append(key)

            if len(disqualifications)== 0:
                disqualifications.append('-1')

            print(f'My disqualifications from card validation: {disqualifications}')


            sendKey(connection,pickle.dumps(disqualifications, -1),reg_private_key)     #s7 -caller list of disq

            pickl = recvKey(connection,sv_public_key)[0]                                #r5c - all list of disq
            disqArrofArr = pickle.loads(pickl) #data loaded.



            votes = []
            for i in range(len(disqArrofArr)):
                for j in disqArrofArr[i]:
                    if j != '-1':
                        votes.append(j)

            counter = Counter(votes)

            final = []
            for key in counter:
                if counter[key] >= (dictlen/2):
                    final.append(key)

            for i in final:
                clean.append(i)
            print(final)

            print(f'Final disqualifications (most agreed on) from card validation: {disqualifications}')
            sendKey(connection,pickle.dumps(final, -1), reg_private_key)           #s1c - final arr of disq (most agreed on)


            msg = ''
            if len(final)==0:
                msg = 'All player cards validated!'
            else:
                for i in final:
                    msg = msg + f'Player {i}: {playerProfiles[i][0]} disqualified for invalid card!\n'

            sendMsg(connection,msg,reg_private_key)                                     #s2c - disq messages

            print(recvMsg(connection, sv_public_key)[0])                                   #r9 - broadcast disq
            

        
            ##### DECK GENERATION

            print(f'\n\n')
            print(recvMsg(connection,sv_public_key)[0])                             #r10- rules 2

            symKey = symKeyGen()
            
            if random.randint(0, 100) <= 10:
                deck = deckGenCHEAT()
                print("I'm cheating this game.")
            else:
                deck = deckGen()

            print(deck)

            startingDeck = CallerEncryptnShuffle(symKey,deck)
            signature = signMsg(reg_private_key,b''.join(startingDeck))

            sendKey(connection,pickle.dumps(startingDeck, -1),reg_private_key)        # s8- starting deck
            sendKey(connection,symKey,reg_private_key)                               #s9 - key
            sendKey(connection,signature,reg_private_key)                               #s10 -sign

            print('Sending initial deck to begin encryption chain...')
            finaldeck = pickle.loads(recvKey(connection,sv_public_key)[0])                  #r6c
            lastDeckSign = signMsg(reg_private_key,b''.join(finaldeck))
            sendKey(connection,lastDeckSign,reg_private_key)       #s3c  

        
            #DECK VALIDATION
            deckDict = pickle.loads(recvKey(connection,sv_public_key)[0])                 #r(11)12 dict

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
                if validation == False:
                    if key != '0':       #not admiting to cheat
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
                        if key != '0':       #not admiting to cheat
                            disqualifications.append(key)

            if len(disqualifications) == 0:
                disqualifications.append('-1')

            ## validations done
            #getting deck:
            finalDeck_afterDecrypt = chainDecrypt(arrSymKeys,finaldeck,0)
            print(f'My disqualifications from deck validation: {disqualifications}\n')
            print(f'Final deck: {finalDeck_afterDecrypt}')


            sendKey(connection,pickle.dumps(disqualifications, -1),reg_private_key)     #s11 disqualifications from deck val
    

          

            ##disqualifications
            disqArrofArr = pickle.loads(recvKey(connection,sv_public_key)[0])                                #r7c - all list of disq

      
            votes = []
            for i in range(len(disqArrofArr)):
                for j in disqArrofArr[i]:
                    if j != '-1':
                        votes.append(j)

            counter = Counter(votes)

            final = []
            for key in counter:
                if counter[key] >= (len(deckDict)/2):
                    final.append(key)

            for i in final:
                clean.append(i)

            print(f'Final disqualifications (most agreed on) from deck validation: {final}')
            temp = final

            if len(final)==0:
                temp=['-1']

            sendKey(connection,pickle.dumps(temp, -1), reg_private_key)           #s4c - final arr of disq (most agreed on)
   

            msg = ''
            if len(final) == 0:
                msg = 'All deck encryptions validated!'
            else:
                for i in final:
                    msg = msg + f'Player {i}: {playerProfiles[i][0]} disqualified for tampering with the process of deck creation!\n'
                msg = msg + f'Due to the modification of the deck compromising the integrity of the game, the game will now abort.'
                sendMsg(connection,msg,reg_private_key)                                     #s5c - disq messages
                print(msg)
                break

            sendMsg(connection,msg,reg_private_key)                                     #s5c - disq messages


            print(recvMsg(connection, sv_public_key)[0])                                   #r13 - broadcast disq
            



            sendKey(connection,pickle.dumps(finalDeck_afterDecrypt, -1),reg_private_key)             #s12 final deck

            allDecks = pickle.loads(recvKey(connection,sv_public_key)[0])                           #r8c

            msg = ''
            if len(list(allDecks))!= 1:
                sendMsg(connection,'Valid',reg_private_key)                                     #s6c - game valid
                msg = f"\nHere's the final deck!\n{finalDeck_afterDecrypt}\nGood luck!"       
                sendMsg(connection,msg,reg_private_key)                                         #s7c - msg
                                                    
            else:
                sendMsg(connection,'Invalid',reg_private_key)                                   #s6c - game valid
                msg = 'Cheating is not to be taken lightly!\nGame will be aborted due to invalid deck distribution'
                sendMsg(connection,msg,reg_private_key)                                         #s7c - msg

            print(msg)  
            winners = {}
            #winners = {seq: index of deck where card finished}

            for key in playerCards:
                seq = key
                username = playerProfiles[key][0]
                card = playerCards[key][0]
                numbersHere = {}

                for i in range(len(finalDeck_afterDecrypt)):
                    if finalDeck_afterDecrypt[i] in card:
                        numbersHere[i] = 'True'
                    else:
                        pass
                
                if len(numbersHere) == len(card):
                    lastNum = list(numbersHere)[-1]
                    winners[str(seq)] = (lastNum+1)
                else:
                    winners[str(seq)] = '-1'
                
                numbersHere.clear()



            sendKey(connection,pickle.dumps(winners, -1),reg_private_key)               #s13  - winners
  

            playerWinners = pickle.loads(recvKey(connection,sv_public_key)[0])          #r9c

            outcomeDisq = []
            for outcomeKey in playerWinners:
                playerout = playerWinners.get(outcomeKey)
                if playerout[0] != winners:
                    outcomeDisq.append(outcomeKey)



            #cleaning winners Array
            for disq in outcomeDisq:
                if disq in winners == True:
                    clean.append(disq)
            for entry in winners:
                if winners.get(entry) == '-1':
                    clean.append(entry)


            for i in range(len(clean)):
                if clean[i] in winners:
                    del winners[clean[i]]
    
    
            print(f'Final disqualifications from outcome validation {outcomeDisq}\n')


            msg = ''
            if len(outcomeDisq) == 0:
                msg = 'Valid'
            else:
                for i in outcomeDisq:
                    msg = msg + f'Player {i}: {playerProfiles[i][0]} disqualified for invalid outcome message!\n'

            sendKey(connection,pickle.dumps(outcomeDisq,-1),reg_private_key)            #s8c - disq dict
            sendMsg(connection,msg,reg_private_key)                                     #s9c - disq messages
            

            sortedResults = sorted(winners.items(), key=lambda x:x[1])

            
            finalWinners = dict(sortedResults)
            
            winMsg = ''
            if len(finalWinners) == 0:
                winMsg = "Sorry, no one's a winner this game. Better luck next time!"
            else:
                winMsg = 'Congrats to these players for winning this game of pyBingo!'
                for i in range(1,len(finalWinners)+1):
                    winner = list(finalWinners.keys())[i-1]
                    winMsg += f'\n{i} place - Player {winner}: won at position {finalWinners.get(winner)}!'

            print(winMsg)
            
            outcomeSignature = signMsg(reg_private_key, winMsg.encode('utf-8'))


            sendMsg(connection, winMsg, reg_private_key)
            sendKey(connection,outcomeSignature,reg_private_key)                        #s14  -signature

            time.sleep(300)

            break
        
        
        except:
            break




     



caller = Caller()
caller.startConnection(dataHandler)
