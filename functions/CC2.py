import datetime
import PyKCS11
from sys import platform
from cryptography import x509
from cryptography.x509 import *
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1, Hash
from crl_checker import check_revoked_crypto_cert, Revoked, Error




def get_system_lib():
        if platform == "linux" or platform == "linux2":
            lib = "/usr/local/lib/libpteidpkcs11.so"
        elif platform == "darwin":
            lib = "/usr/local/lib/libpteidpkcs11.dylib"
        elif platform == "win32":
            lib = "C:\Windows\System32\pteidpkcs11.dll"
        return lib



class  CC:

    def __init__(self):
        #init of Citizen card, load its data and start session
      
        self.validation = False
        pkcs11 = PyKCS11.PyKCS11Lib()
        pkcs11.load(get_system_lib())
        

        while True:
            slots = pkcs11.getSlotList()
            if (len(slots)!=0):
                self.session = pkcs11.openSession(slots[0])
                break
            else:
                print("[ENDING CONNECTION] Connection denied due to missing authentication. Please connect your smartcard.")
                self.validation = False
                break
        



    def get_certificate_data(self,label):
        #[CITIZEN AUTHENTICATION CERTIFICATE]
        #[SIGNATURE SUB CA]
        #[AUTHENTICATION SUB CA]
        #[ROOT CA]
        #[CITIZEN SIGNATURE CERTIFICATE]
        if label == "CITIZEN AUTHENTICATION CERTIFICATE":
            cert_obj = self.session.findObjects([
                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
                    (PyKCS11.CKA_LABEL, label)
                    ])[0]
        else:
            cert_obj = self.session.findObjects([
                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
                    (PyKCS11.CKA_LABEL, label)
                    ])

        cert_der_data = bytes(cert_obj.to_dict()['CKA_VALUE'])
        data = x509.load_der_x509_certificate(cert_der_data)  
        return data     



    def validate_dates(self,cert):
        if (cert.not_valid_before <= datetime.datetime.now() <= cert.not_valid_after):
            return True
        else:
            return False



    def crl_check(self,cert):
        try:
            check_revoked_crypto_cert(cert)
        except Revoked as e:
            return False
        except Error as e:
            return False
        return True



#validate CC!

    def validate_certificate_chain(self):

        cert = self.get_certificate_data('CITIZEN AUTHENTICATION CERTIFICATE')
        #from client
        if ((self.crl_check(cert) & self.validate_dates(cert)) == True):
                try:
                    cert.public_key().verify(
                            cert.signature,
                            cert.tbs_certificate_bytes,
                            PKCS1v15(),
                            cert.signature_hash_algorithm,
                            )
                except InvalidSignature:
                        return False           

        #chain
        while True:
            issuer = cert.issuer
            if issuer == cert.subject:
                # Self-signed certificate found
                break

            # Load the issuer certificate
            issuer_cert = self.get_certificate_data('AUTHENTICATION SUB CA')

            if ((self.validate_dates(issuer_cert)) == False):
                return False
            
            if issuer_cert.subject != issuer:
                # Certificate chain is invalid
                return False

            # Check if the issuer certificate was signed by the current certificate
            try : issuer_cert.public_key().verify(
                            cert.signature,
                            cert.tbs_certificate_bytes,
                            PKCS1v15(),
                            cert.signature_hash_algorithm,
                            )

            except InvalidSignature:
                return False 

            # Move to the next certificate in the chain
            cert = issuer_cert
   

        # Check if the self-signed certificate is in the list of trusted root CAs
        root_ca_cert = self.get_certificate_data('ROOT CA')

        if ((self.validate_dates(root_ca_cert)) == False):
                return False

        if cert.issuer != root_ca_cert.subject:
            # Certificate chain is not trusted
            return False

        return True


#external use

### Wrong
    def public_key(self):
        self.public_key = self.session.findObjects([
                                        (PyKCS11.CKA_CLASS, PyKCS11.CKO_PUBLIC_KEY),
                                        (PyKCS11.CKA_LABEL, 'CITIZEN AUTHENTICATION KEY')
                                        ])[0]
        return self.public_key

    def private_key(self):
        self.private_key =  self.session.findObjects([
                                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                                    (PyKCS11.CKA_LABEL, 'CITIZEN AUTHENTICATION KEY')
                                    ])[0]
        return self.private_key

