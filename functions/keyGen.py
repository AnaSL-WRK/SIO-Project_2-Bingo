import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization




def keyGen():
    
    key = rsa.generate_private_key(public_exponent=65537,key_size=1024)

    pemPriv = key.private_bytes(encoding=serialization.Encoding.PEM,
                                format=serialization.PrivateFormat.TraditionalOpenSSL,
                                encryption_algorithm=serialization.NoEncryption()
                                )


    public_key = key.public_key()
    pemPub = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                    format=serialization.PublicFormat.SubjectPublicKeyInfo)

    return pemPriv, pemPub



def symKeyGen():

  key = os.urandom(16)
  return key

