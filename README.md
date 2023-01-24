# Project 2 SIO [2022-2023]
## Secure Game - Bingo

### Author:

| **Nmec** | **Name**     | **Course** | **Email**    | **Project grade**|
|----------|--------------|------------|--------------|------------------|
| 104063   | Ana Loureiro |   [LEI]    | ana.sl@ua.pt |19.8|


### Project Description:

This assignment will focus on the implementation of a robust protocol for handling a distributed game. The game under study will be Bingo, which is a game of chance. Implementation will consist of a server (Playing Area) and multiple clients (one caller and multiple players) communicating over a network.

### Objective of the game:

The game in question is Bingo,a game that can take a variable number of players. Each player decides on a card, made up of 12 numbers from 0 to 48, and then follows the order of the game's deck, crossing the numbers the player has on its card. To win, you have to complete your card the fastest, according to the game's deck, so a game can have multiple winners if they end on the same position.

### Components:

Each of the projects folder contains a README file, describing the role of each component.

- Playing Area's [README.md](Playing%20Area/README.md)
- Player's [README.md](Player/README.md)
- Caller's [README.md](Caller/README.md)

At the end of this file, each function in the [functions](functions/) folder will be documented.

### Implementation and flow of the game:

#### Implementation:
The server runs using Python sockets, running on Threads. Each connection runs using TCP protocol, wrapped in SSL to provide stable security on the connection throughout the game.

#### Game:

A client (player or caller) can only connect to the playing area (server) if they provide a valid Portuguese Citizen Card certificate, being denied connection otherwise. After choosing their username and being provided of their sequence number and public key to sign their exchanged messages, their registration is complete, outputing a file containing their game information, Citizen Card certificate, and being signed with it's key.  

After being provided the rules, each player creates its card for the game and signs it, commiting it to the playing area. After every card is commited, they are sent back to the players and the caller, now having access over every player's card. If any card is deemed invalid, a vote takes place where the majority of players have to agree that the player in question was in fact cheating in order to get kicked by the caller.

After the card validation process is done, the player receives the second set of rules for the deck handling. In order to keep the game's integrity (deny opportunity for either the players or the caller to cheat the deck), a first set of numbers is shuffled and encrypted by the caller (using a newly created symmetric key), signing it and passing it on to the next player (sequencial order), exchanging it through the playing area. This process repeats for every player (shuffle, encrypt, sign, passing to the next player) until it finally reaches the caller again, who will sign this final encrypted deck.

After this process is done, this deck is provided and posted to each player, along with every player's information (sequence, username, public key, symmetric key and deck he encrypted and signature), having now to decrypt in reverse order and validate it (by checking the signature and also if the deck the player encrypted matches the decryption of the previous one). Player's also have verify if the caller didn't cheat, using the same information. If it was decided that the caller cheated, the player is given the option to leave the game.
If the caller detects if any player tampered with the deck, he has the decision to abort the game due to the deck having lost its integrity.

Now reaching the final deck, players have again to check if the caller cheated on it as well (invalid size or numbers), having again the option to leave the game if true, while the caller has to verify if every player reached the same final deck, aborting the game if negative.

In the end, every player checks for the winners, having all to arrive at the same outcome, being disqualified by the caller if otherwise.


## Functions Documentation

### addvalDict.py -  [file](functions/addvalDict.py)
This file handles the creation of dictionaries with arrays as items, containing:

- **addValDict** used to agreggate all players responses into one dictionary, for easier handling.  
- **getKeyDict**  a function to get the key given an item.

 <br> 

### cardGen.py -  [file](functions/cardGen.py)
This file handles the creation of player cards as well as the deck, containing options to use in case of cheating:

- **cardGen** used to create a valid player card (12 numbers in [0,48])  
- **cardGenCHEAT**  used to create an invalid player card, having 50% chance to create a card with 3 repeated numbers, or a card with an invalid length of 15

- **deckGen** used to create a valid game deck (48 numbers in [0,48])  
- **deckGenCHEAT**  used to create an invalid game deck, having 50% chance to create a deck with 8 repeated numbers, or a game deck with an invalid length of 56 [0,64].

 <br> 


### CC2.py -  [file](functions/CC2.py)
This file handles validation of the Citizen Card, containing:

- **get_system_lib** used to retrieve the library used to access the Portuguese Citizen Card (having its path being dependent on the system it runs)

It then contains the entity CC, with the functions:

- **get_certificate_data**  used to retrieve and load the data of the chosen certificate.

- **validate_dates** used to validate expiring date of the certificate (not_valid_before and not_valid_after).
  
- **crl_check**  used to check if the certificate has been revoked or not.

- **validate_certificate_chain** used to validate the given certificate, using the chain validation of itself, SUB CA Certificate and ROOT CA Certificate.

 <br> 

### deckHandle.py -  [file](functions/deckHandle.py)
This file handles the chain encryption and decryption of the deck, containing:

- **CallerEncryptnShuffle** used by the caller to shuffle the numbers and converting them to bytes, creating an iv for each number to encrypt and prepending it to the number. It the encrypts each number separately and returns the array.

- **EncryptnShuffle**  does the same as the function above, only now it isn't needed to convert the numbers to bytes (used by the players).

- **decrypt** used to decrypt a deck, given the key. It separates the iv and number for each block, allowing it be decrypted and adds it to the returning array (used to decrypt a single deck).
  
- **chainDecrypt**  a recursive function that does the same as the above, only now it accepts an array of keys and the final encrypted deck. In the end it converts the bytes back to numbers, returning the final deck. (used easily obtain the needed deck for the game).

 <br> 

### keyGen.py -  [file](functions/keyGen.py)
This file handles the creation of symmetric keys and assymetric key pairs:

- **keyGen** returns a new pair of assymetric keys (RSA key pairs) (used by everyone to sign their messages, cards and decks).

- **symKeyGen**  returns a symmetric key (used during the deck encryption and decryption process).

 <br> 

### logger.py -  [file](functions/logger.py)
This file handles the logging done by the Playing Area, containing:

- **HashgetLastLine** used to read the last line from the log file (if it exists) and hashing it (contained in the log).

- **log**  creates a log entry with the parameters [seq, asctime, hash, msg, signature)], used by the Playing Area


 <br> 

 ### msgHandle.py -  [file](functions/msgHandle.py)
This file handles the communication between connections, containing:

- **sendMsg** used by the users to send their string message, along with their signature.
  
- **recvMsg**  used by the users to receive the string message, along with the signature, and validating it, returning the message and the bool from validation.
  
- **sendKey/recvKey** functions with the same purpose of the above ones, only now the message doesn't get encoded/decoded (used to send byte messages, like keys or pickled information).

 <br> 
  
- **PAsendMsg**  used by the Playing Area to redirect string messages, along with their signature as well as logging it.

- **PArecvMsg**  used by the Playing Area to receive the string message, along with the signature, and validating it, returning the message and the bool from validation, logging these entries as well. In case the function returns empty, the connection with its sender is terminated.
  
- **PAsendKey/PArecvKey** functions with the same purpose of the above ones, only now the message doesn't get encoded/decoded (used to send byte messages, like keys or pickled information).
  
- **pickleLoad** handles the loading of a pickled message, returning an empty array if an exception is caught
  
 <br> 


### signature.py -  [file](functions/signature.py)
This file handles the signature and validation of messages, containing:

- **signMsg** returning the signature of the message done with the given key

- **verifySignature**  verifies the signature, given the public key, message and signature, returning a bool.


 <br> 

### timer.py -  [file](functions/timer.py)
This file handles the timer feature for the initiation of the game:

- **countdown** returning '0' when the time (given minutes and seconds) end.

 <br> 
