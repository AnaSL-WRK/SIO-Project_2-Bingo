# Playing Area

This folder contais the [Server code](server.py) and [Playing Area](playingArea.py).  

In order to be able to start game, this is the first folder you need to run.

## How to run
- First, make sure you have the required modules installed.  
For that, using your terminal, navigate to the root folder, where [requirements.txt](./../requirements.txt) is located.  
Then run the code ```sudo pip install -r requirements.txt```, and you should get all necessary modules to run this project.  

- To start the server simply run ```python3 playingArea.py``` (depending on your version of python you might have to do ```python playingArea.py``` )

And you're all set!

## What is the Playing Area
 
The Playing Area is the server of the game, to which all users connect and acts as a secure playing field. It redirects the messages to all, while signing them for authenticity.  

It stores the following actions:
- logs every message exchanged, stored in the file [log.log](log.log)
- saves the user profiles of the game, storing them in [Player_profiles.txt](Player_profiles.txt).
- stores the registration messages done for every player that played the game, located in the folder [Registrations](Registrations/).