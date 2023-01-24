import logging
import os
from cryptography.hazmat.primitives import hashes

def log(extra,msg):
    
    logging.basicConfig(
                    level=logging.INFO,
                    format='%(seq)s %(asctime)s %(hash)s %(msg)s %(signature)s',
                    datefmt='%d/%m/%Y %I:%M:%S',
                    filename="log.log",
                    filemode="a",)


    logger = logging.getLogger()

    logger = logging.LoggerAdapter(logger, extra)
    logger.info(msg)


def HashgetLastLine():
    digest = hashes.Hash(hashes.SHA256())
    with open("log.log", "rb") as file:
        try:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:
            if file.seek(0) == None:
                last_line = None
            else:
                last_line = file.seek(0)

        last_line = file.readline()
        digest.update(last_line)
        hashed = digest.finalize()


    return hashed

