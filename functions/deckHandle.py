import secrets,random
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


def CallerEncryptnShuffle(key,array):

    encArray = []
    random.shuffle(array)
    for num in array:

        iv = secrets.token_bytes(16)
        num = int.to_bytes(num, 2,'little')
        num = iv + num

        cipher = Cipher(algorithms.AES(key),modes.CFB(iv))
        encryptor = cipher.encryptor()

        num = encryptor.update(num) + encryptor.finalize()
        encArray.append(num)

    
        

    return encArray


def EncryptnShuffle(key,array):

    encArray = []
    random.shuffle(array)
    for num in array:

        iv = secrets.token_bytes(16)
        num = iv + num

        cipher = Cipher(algorithms.AES(key),modes.CFB(iv))
        encryptor = cipher.encryptor()

        num = encryptor.update(num) + encryptor.finalize()
        encArray.append(num)

    

    return encArray


def decrypt(key,array):

    decArray = []

    for num in array:

        iv = num[:16]
        dec = num[16:]

        cipher = Cipher(algorithms.AES(key),modes.CFB(iv))
        decryptor = cipher.decryptor()

        dec = decryptor.update(dec) + decryptor.finalize()
        decArray.append(dec)

    return decArray





def chainDecrypt(arrKeys,block,index):

    key = arrKeys[index]

    newblock = decrypt(key,block)
    if not(0 <= index < len(arrKeys)-1):
        finalDeck = []
        for i in range(len(newblock)):
            num = int.from_bytes(newblock[i],'little')
            finalDeck.append(num)
        return finalDeck
        
    else:
        return(chainDecrypt(arrKeys,newblock,index+1))