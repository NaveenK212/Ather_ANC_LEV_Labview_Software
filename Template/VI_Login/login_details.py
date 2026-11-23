import sys
import configparser
from cryptography.fernet import Fernet

# Encrypt a value
def encrypt_value(cipher, value):
    return cipher.encrypt(value.encode()).decode()

# Decrypt a value
def decrypt_value(cipher, value):
    return cipher.decrypt(value.encode()).decode()

def read_ini(file_name, cipher, user_type=None, specific_username=None):
    config = configparser.ConfigParser()
    config.read(file_name)
    if 'login' not in config:
        return {}, {}

    admin_data = {'usernames': [], 'passwords': []}
    developer_data = {'usernames': [], 'passwords': []}

    for key, value in config['login'].items():
        decrypted_value = decrypt_value(cipher, value)
        if key.startswith("admin") and "_user_name" in key:
            if specific_username and user_type == "admin" and decrypted_value == specific_username:
                # Get the corresponding password
                password_key = key.replace("_user_name", "_password")
                password = decrypt_value(cipher, config['login'].get(password_key, ""))
                return {"username": decrypted_value, "password": password}
            admin_data['usernames'].append(decrypted_value)
        elif key.startswith("admin") and "_password" in key:
            admin_data['passwords'].append(decrypted_value)
        elif key.startswith("developer") and "_user_name" in key:
            if specific_username and user_type == "developer" and decrypted_value == specific_username:
                # Get the corresponding password
                password_key = key.replace("_user_name", "_password")
                password = decrypt_value(cipher, config['login'].get(password_key, ""))
                return {"username": decrypted_value, "password": password}
            developer_data['usernames'].append(decrypted_value)
        elif key.startswith("developer") and "_password" in key:
            developer_data['passwords'].append(decrypted_value)

    # Return categorized data or a blank dictionary if specific_username is provided but not found
    if specific_username:
        return {}

    return admin_data, developer_data


# Write updated data back to the INI file
def write_ini(file_name, cipher, data):
    config = configparser.ConfigParser()
    config['login'] = {key: encrypt_value(cipher, value) for key, value in data.items()}
    with open(file_name, 'w') as configfile:
        config.write(configfile)

# Add a new user to the INI file
def add_user(file_name, cipher, user_type, username, password):
    config = configparser.ConfigParser()
    config.read(file_name)

    # Generate next index for the user
    existing_keys = [key for key in config['login'].keys() if key.startswith(user_type)]
    next_index = len(existing_keys) // 2 + 1  # Divide by 2 because of username and password pairs

    # Add the new user
    config['login'][f"{user_type}_{next_index}_user_name"] = encrypt_value(cipher, username)
    config['login'][f"{user_type}_{next_index}_password"] = encrypt_value(cipher, password)

    # Write back to the INI file
    with open(file_name, 'w') as configfile:
        config.write(configfile)
    print("successfully.")

# Update password for an existing user
def update_password(file_name, cipher, user_type, username, new_password):
    config = configparser.ConfigParser()
    config.read(file_name)

    for key, value in config['login'].items():
        decrypted_value = decrypt_value(cipher, value)
        if key.startswith(user_type) and "_user_name" in key and decrypted_value == username:
            # Identify the corresponding password key
            password_key = key.replace("_user_name", "_password")
            if password_key in config['login']:
                config['login'][password_key] = encrypt_value(cipher, new_password)
                with open(file_name, 'w') as configfile:
                    config.write(configfile)
                print(f"successfully")
                return

    print(f"Username '{username}' not found in {user_type} users.")

# Main function
def main():
    if len(sys.argv) < 3:
        print("Usage: script.py <encryption_key> [add|read|update] <type> <username> [<password/new_password>]")
        sys.exit(1)

    encryption_key = sys.argv[1]
    cipher = Fernet(encryption_key)

    ini_file = 'credentials.ini'
    # ini_file = "D:\Projects\BEL\BEL_SDR_MANPACK_LabVIEW_Software\Data\credentials.ini"

    if sys.argv[2] == "read":
        if len(sys.argv) == 4:
            # Read all users for a specific type
            user_type = sys.argv[3].lower()
            admin_data, developer_data = read_ini(ini_file, cipher)
            if user_type == "admin":
                print(",".join(admin_data['usernames']))
                print(",".join(admin_data['passwords']))
            elif user_type == "developer":
                print(",".join(developer_data['usernames']))
                print(",".join(developer_data['passwords']))
            else:
                print("Invalid user type. Use 'admin' or 'developer'.")
        elif len(sys.argv) == 5:
            # Read a specific user's credentials
            user_type = sys.argv[3].lower()
            username = sys.argv[4]
            result = read_ini(ini_file, cipher, user_type, username)
            if result:
                print(f"{result['username']}")
                print(f"{result['password']}")
            else:
                print(f"User '{username}' not found in {user_type} users.")
    
    elif sys.argv[2] == "add":
        if len(sys.argv) != 6:
            print("Usage: script.py <encryption_key> add <admin|developer> <username> <password>")
            sys.exit(1)

        user_type = sys.argv[3].lower()
        if user_type not in ("admin", "developer"):
            print("Invalid user type. Use 'admin' or 'developer'.")
            sys.exit(1)

        username = sys.argv[4]
        password = sys.argv[5]
        add_user(ini_file, cipher, user_type, username, password)
    elif sys.argv[2] == "update":
        if len(sys.argv) != 6:
            print("Usage: script.py <encryption_key> update <admin|developer> <username> <new_password>")
            sys.exit(1)

        user_type = sys.argv[3].lower()
        if user_type not in ("admin", "developer"):
            print("Invalid user type. Use 'admin' or 'developer'.")
            sys.exit(1)

        username = sys.argv[4]
        new_password = sys.argv[5]
        update_password(ini_file, cipher, user_type, username, new_password)

if __name__ == "__main__":
    main()
