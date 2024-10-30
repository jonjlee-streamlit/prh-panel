"""
Symmetric encryption and decryption using Fernet.
Run this file directly to print out a new randomly generated key.
"""

import sys, os
import logging
import requests
from cryptography.fernet import Fernet


def encrypt(data: bytes, key: str) -> bytes:
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    return encrypted


def encrypt_file(file: str, outfile: str, key: str):
    with open(file, "rb") as f:
        data = f.read()
    encrypted = encrypt(data, key)
    with open(f"{outfile}", "wb") as f:
        f.write(encrypted)


def decrypt(data: bytes, key: str) -> bytes:
    fernet = Fernet(key)
    decrypted = fernet.decrypt(data)
    return decrypted


def decrypt_file(file: str, outfile: str, key: str):
    with open(file, "rb") as f:
        data = f.read()
    decrypted = decrypt(data, key)
    with open(f"{outfile}.dec", "wb") as f:
        f.write(decrypted)


# Run as script. With no parameters, will generate a new key. Use -key to specify key to use,
# and -encrypt <file> or -decrypt <file> to encrypt / decrypt a file to disk
# Use -out <file> to specify output filename, otherwise will default to <file>.enc or <file>.dec
if __name__ == "__main__":
    if "-help" in sys.argv or "--help" in sys.argv:
        print('Accepted parameters: -key, -encrypt <file>, -decrypt <file>, -out <file>.\nIf -out is not specified, will default to <file>.enc or <file>.dec')
        exit(0)

    # Accept the -key parameter, or generate a new key
    if "-key" in sys.argv:
        key = sys.argv[sys.argv.index("-key") + 1]
        print("Using provided key")
    else:
        key = Fernet.generate_key().decode("utf-8")
        print(key)

    # store output file from -out parameter
    if "-out" in sys.argv:
        out = sys.argv[sys.argv.index("-out") + 1]
    else:
        out = None

    # if -encrypt <file> parameter, encrypt the specified file
    if "-encrypt" in sys.argv:
        file = sys.argv[sys.argv.index("-encrypt") + 1]
        if os.path.exists(file):
            out = out if out is not None else file + ".enc"
            encrypt_file(file, out, key)
            print(f"Encrypted {file} -> {out}")

    # if -decrypt <file> parameter, decrypt the specified file
    if "-decrypt" in sys.argv:
        file = sys.argv[sys.argv.index("-decrypt") + 1]
        if os.path.exists(file):
            out = out if out is not None else file + ".dec"
            decrypt_file(file, out, key)
            print(f"Decrypted {file} -> {out}")
