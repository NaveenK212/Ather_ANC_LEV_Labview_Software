import configparser
from cryptography.fernet import Fernet
import os
import argparse
#python Create_User.py --name operator --password operator --role operator
#python Create_User.py --name admin --password admin --role admin
# =====================================================
# FILE PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INI_FILE = os.path.join(BASE_DIR, "users.ini")
KEY_FILE = os.path.join(BASE_DIR, "secret.key")

# =====================================================
# LOAD / CREATE KEY
# =====================================================

def load_key():

    if not os.path.exists(KEY_FILE):

        key = Fernet.generate_key()

        with open(KEY_FILE, "wb") as f:
            f.write(key)

        print("secret.key created")

    else:

        with open(KEY_FILE, "rb") as f:
            key = f.read()

    return key

# =====================================================
# ADD USER
# =====================================================

def add_user(username, password, role):

    key = load_key()

    cipher = Fernet(key)

    encrypted_password = cipher.encrypt(
        password.encode()
    ).decode()

    config = configparser.ConfigParser()

    config.optionxform = str

    # Read existing file
    if os.path.exists(INI_FILE):

        config.read(INI_FILE)

    # Create role section if not exists
    if role not in config.sections():

        config[role] = {}

    # Check duplicate user
    if username in config[role]:

        print(f"User '{username}' already exists under '{role}'")
        return

    # Save user under role
    config[role][username] = encrypted_password

    # Write file
    with open(INI_FILE, "w") as configfile:

        config.write(configfile)

    print(f"User '{username}' saved successfully under '{role}'")

# =====================================================
# SHOW USERS
# =====================================================

def show_users():

    config = configparser.ConfigParser()

    config.optionxform = str

    if not os.path.exists(INI_FILE):

        print("No users found")
        return

    config.read(INI_FILE)

    print("\nSaved Users")
    print("----------------")

    for section in config.sections():

        print(f"\n[{section}]")

        for user in config[section]:

            print(user)

# =====================================================
# ARGUMENTS
# =====================================================

parser = argparse.ArgumentParser()

parser.add_argument("--name")
parser.add_argument("--password")
parser.add_argument(
    "--role",
    choices=["admin", "operator"]
)

parser.add_argument(
    "--showusers",
    action="store_true"
)

args = parser.parse_args()

# =====================================================
# MAIN
# =====================================================

if args.showusers:

    show_users()

elif args.name and args.password and args.role:

    add_user(
        args.name,
        args.password,
        args.role
    )

else:

    print("\nAdd User:")
    print(
        "python add_user.py --name admin --password 1234 --role admin"
    )

    print("\nShow Users:")
    print(
        "python add_user.py --showusers"
    )
