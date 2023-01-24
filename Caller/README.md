# Caller

This folder contais the [Caller connection handler](caller.py) and [Caller code](main.py).  

In order for a game to start, it is required for the server to be running, a caller to be present and at least one player to be present.

The caller can connect while there's still no players present, having to wait for one to connect.

## How to run
- First, make sure you have the required modules installed.  
For that, using your terminal, navigate to the root folder, where [requirements.txt](./../requirements.txt) is located.  
Then run the code ```sudo pip install -r requirements.txt```, and you should get all necessary modules to run this project.  

- To start the caller, make sure you have the [Playing Area](../Playing%20Area/) already running and simply run the command ```python3 main.py``` on another terminal (depending on your version of python you might have to do ```python main.py``` )

And you're all set!

## What is the Caller
The caller should be a Portuguese citizen, as this game requires Citizen Card validation. The playing area can only have one caller, but any player can act as a caller.

The caller will be identified by the sequence number '0', a public key and a nickname.

Each callers’s public key belongs to an asymmetric key pair generated for them just for playing (provided in the login process)

The caller as special privileges, not being able to participate on the game itself (they have no card to play the game) but provide authentication and ruling over the game.

The caller has the power to disqualify and disconnect players, as well as abort the game when it's integrity has been compromised.

The caller will also participate on the creation of the deck and verify the winners in group, no cheating tolerated!

Good Luck!