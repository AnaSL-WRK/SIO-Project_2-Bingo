# Player

This folder contais the [Player connection handler](client.py) and [Player code](main.py).  

In order for a game to start, it is required for the server to be running, a caller to be present and at least one player to be present.

## How to run
- First, make sure you have the required modules installed.  
For that, using your terminal, navigate to the root folder, where [requirements.txt](./../requirements.txt) is located.  
Then run the code ```sudo pip install -r requirements.txt```, and you should get all necessary modules to run this project.  

- To start the client, make sure you have the [Playing Area](../Playing%20Area/) already running and simply run the command ```python3 main.py``` on another terminal (depending on your version of python you might have to do ```python main.py``` )

And you're all set!

## What is the Player
The player should be a Portuguese citizen, as this game requires Citizen Card validation. While the playing area can only have one caller, there is no limit for the amount of players that can join (although the number affects the processing speed of the game).

Each player will be identified by a sequence number, a public key and a nickname.

Each players’s public key belongs to an asymmetric key pair generated for them just for playing (provided in the login process)

Each player will have a card, participate on the creation of the deck and verify the winners in group, no cheating tolerated!

Good Luck!