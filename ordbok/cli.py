from __future__ import print_function
import os
import argparse
from .ordbok import Ordbok
from .config_private import PrivateConfigFile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        help="Available commands are `encrpyt` or `decrypt`.")
    parser.add_argument(
        "file",
        help=("The file to be encrypted or decrypted. the `.private` can be "
              "left off when decrypting."))
    parser.add_argument(
        "key",
        help="The key used to encrypt or decrypt the file.")

    args = parser.parse_args()

    filename = args.file

    private_config_file = PrivateConfigFile(filename)
    ordbok = Ordbok(custom_config_class=[private_config_file], config_dir='')
    ordbok['PRIVATE_KEY_ORDBOK'] = args.key
    private_config_file.init_config(ordbok)

    if args.command == "encrypt":
        private_config_file._save_encrypted_file()
        os.remove(private_config_file.config_file_path)
        print('{}.private created'.format(private_config_file.filename))
    elif args.command == "decrypt":
        private_config_file._save_decrypted_file()
        os.remove(private_config_file.config_file_path+'.private')
        print('{} created'.format(filename))
    else:
        print('unknown command')


if __name__ == "__main__":
    main()
