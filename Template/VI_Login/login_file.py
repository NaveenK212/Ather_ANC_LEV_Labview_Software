import sys
import configparser
from cryptography.fernet import Fernet

# Generate a key for encryption and decryption (store this securely)
key = sys.argv[1]
cipher = Fernet(key)

admin_username=sys.argv[2]
admin_Password=sys.argv[3]
dev_username=sys.argv[4]
dev_Password=sys.argv[5]

# Create the configuration
config = configparser.ConfigParser()
config['login'] = {
    'admin_User_name': cipher.encrypt(admin_username.encode()).decode(),
    'admin_Password': cipher.encrypt(admin_Password.encode()).decode(),  # Encrypt admin password
    'developer_User_name': cipher.encrypt(dev_username.encode()).decode(),
    'developer_Password': cipher.encrypt(dev_Password.encode()).decode()  # Encrypt developer password
}

# Write the encrypted values to the INI file
with open('credentials.ini', 'w') as configfile:
    config.write(configfile)

print("INI file with encrypted passwords created as 'config.ini'.")
