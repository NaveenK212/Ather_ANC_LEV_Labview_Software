import configparser
from cryptography.fernet import Fernet
import os
import argparse
import sys

# =====================================================
# FIX WINDOWS ENCODING (IMPORTANT FOR LABVIEW)
# =====================================================

sys.stdout.reconfigure(encoding='utf-8')

# =====================================================
# FILE PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INI_FILE = os.path.join(BASE_DIR, "users.ini")
KEY_FILE = os.path.join(BASE_DIR, "secret.key")

# =====================================================
# LOAD KEY
# =====================================================

def load_key():

    if not os.path.exists(KEY_FILE):
        print("KEY_MISSING")
        return None

    with open(KEY_FILE, "rb") as f:
        return f.read()

# =====================================================
# CHECK USER ONLY
# =====================================================

def check_user(username, password, role):

    # FILE CHECK
    if not os.path.exists(INI_FILE):
        print("NO_USERS_FILE")
        return

    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(INI_FILE)

    # ROLE CHECK
    if role not in config.sections():
        print("ROLE_NOT_FOUND")
        return

    # USER CHECK
    if username not in config[role]:
        print("USER_NOT_FOUND")
        return

    # PASSWORD CHECK
    key = load_key()
    if key is None:
        return

    cipher = Fernet(key)

    stored_password = config[role][username]
    decrypted_password = cipher.decrypt(
        stored_password.encode()
    ).decode()

    if password == decrypted_password:
        print("LOGIN_OK")
    else:
        print("PASSWORD_WRONG")

# =====================================================
# ARGUMENTS
# =====================================================

parser = argparse.ArgumentParser()

parser.add_argument("--name", required=True)
parser.add_argument("--password", required=True)

parser.add_argument(
    "--role",
    required=True,
    choices=["admin", "operator"]
)

args = parser.parse_args()

# =====================================================
# MAIN
# =====================================================

check_user(args.name, args.password, args.role)
