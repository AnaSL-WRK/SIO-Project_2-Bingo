from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from keyGen import keyGen


def signMsg(privKey,msg):

    privKeySer = serialization.load_pem_private_key(
                                                privKey,
                                                password=None, 
                                                backend=default_backend())

    signature = privKeySer.sign(
                        msg,
                        padding.PSS(
                                    mgf=padding.MGF1(hashes.SHA256()),
                                    salt_length=padding.PSS.MAX_LENGTH
                                    ),
                        hashes.SHA256()
                    )
 
    return signature




def verifySignature(pubKey,msg,signature):

    pubKeySer = serialization.load_pem_public_key(
                                                pubKey,
                                                backend=default_backend())

    try: pubKeySer.verify(
                            signature,
                            msg,
                            padding.PSS(
                                        mgf=padding.MGF1(hashes.SHA256()),
                                        salt_length=padding.PSS.MAX_LENGTH
                                        ),
                            hashes.SHA256()
                        )

          
    except:
        return False
    return True


