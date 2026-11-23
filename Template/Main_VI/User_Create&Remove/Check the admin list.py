import configparser
from cryptography.fernet import Fernet
import os
import argparse
#--name Rachna --password 1234
# =====================================================
# FILE PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INI_FILE = os.path.join(BASE_DIR, "users.ini")
KEY_FILE = os.path.join(BASE_DIR, "secret.key")

# =====================================================
# LOAD SECRET KEY
# =====================================================

def load_key():

    if not os.path.exists(KEY_FILE):

        print("secret.key file not found")
        exit()

    with open(KEY_FILE, "rb") as f:

        key = f.read()

    return key

# =====================================================
# VERIFY USER
# =====================================================

def verify_user(username, password):

    config = configparser.ConfigParser()

    config.optionxform = str

    # Check INI exists
    if not os.path.exists(INI_FILE):

        print("users.ini file not found")
        return

    # Read INI
    config.read(INI_FILE)

    # Check user exists
    if username not in config.sections():

        print("User does not exist")
        return

    # Load encryption key
    key = load_key()

    cipher = Fernet(key)

    try:

        # Read encrypted password
        encrypted_password = config[username]["password"]

        # Decrypt password
        saved_password = cipher.decrypt(
            encrypted_password.encode()
        ).decode()

    except Exception as e:

        print("Password decryption failed")
        return

    # Verify password
    if saved_password == password:

        print("User exists")

    else:

        print("Wrong password")

# =====================================================
# ARGUMENTS
# =====================================================

parser = argparse.ArgumentParser()

parser.add_argument(
    "--name",
    required=True
)

parser.add_argument(
    "--password",
    required=True
)

args = parser.parse_args()

# =====================================================
# MAIN
# =====================================================

verify_user(
    args.name,
    args.password
)
