import random
#bingo numbers are fom 0-48 and cards have 12 numbers

def cardGen():
    card = random.sample(range(0,49),12)
    return card


def cardGenCHEAT():

    if random.randint(0, 100) <= 50:
        card = random.sample(range(0,49),9)
        getRandom = random.SystemRandom()

        for i in range(3):
            card.append(getRandom.choice(card))

    else:
        card = random.sample(range(0,49),15)


    return card

def deckGen():
    deck = random.sample(range(0,49),48)
    return deck

def deckGenCHEAT():
    if random.randint(0, 100) <= 50:
        deck = random.sample(range(0,49),40)
        getRandom = random.SystemRandom()

        for i in range(8):
            deck.append(getRandom.choice(deck))

    else:
        deck = random.sample(range(0,64),56)

    return deck
