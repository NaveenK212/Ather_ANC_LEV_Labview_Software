import configparser
import sys

def read_ini_file(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)

    if not config.sections():
        print(f"No sections found or file not found: {file_path}")
        return

    for section in config.sections():
        print(f"\n[{section}]")
        for key, value in config.items(section):
            print(f"  {key} = {value}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_ini_file>")
        sys.exit(1)

    read_ini_file(sys.argv[1])
