# Requirements:
# sudo apt install python3 python3-pip -y
# pip3 install boto3
import logging
from boto3 import client
from botocore.exceptions import ClientError
from argparse import ArgumentParser
from os import getenv

class KMSTasks():

    def __init__(self):

        parser = ArgumentParser()      

        parser.add_argument(
        '-f',
        '--filename',
        help='Exemplo: script.py -f "myfile.txt"',
        required=True
        )

        parser.add_argument(
        '-r',
        '--region',
        help='Exemplo: script.py -r "us-east-1". Default = "sa-east-1"',
        required=False,
        default='sa-east-1'
        )
        
        parser.add_argument(
        '-e',
        '--encrypt',
        help='Exemplo: script.py -f "myfile.txt" -e ',
        required = False,
        default = False,
        action = 'store_true'
        )

        parser.add_argument(
        '-d',
        '--decrypt',
        help='Exemplo: script.py -f "myfile.txt" -d ',
        required = False,
        default = False,
        action = 'store_true'
        )

        args = parser.parse_args()
        filename = args.filename
        region = args.region 

        self.kms_client = client('kms', region_name=region)
        try:
            self.kms_client.list_keys()
        except ClientError as e:
            logging.error(e)
            exit()

        self.key_id= getenv('AWS_KMS_KEY_ID', default=None) # Export yout aws kms key id !
        if not self.key_id:
            print('No key id defined. Run: export AWS_KMS_KEY_ID="your-key-id-here"')
        
        if args.encrypt:
            self.run_encrypt(filename)
        elif args.decrypt:
            self.run_decrypt(filename)
        else:
            print("Nothing to do! Set a task option: -e (encrypt) or -d (decrypt)")
            exit()

    def run_encrypt(self, filename):
        try:
            with open(filename, 'rb') as file:
                file_contents = file.read()
        except IOError as e:
            logging.error(e)
            return False

        response = self.kms_client.encrypt(
            KeyId=self.key_id,
            Plaintext=file_contents
        )

        file_contents_encrypted = response['CiphertextBlob']

        try:
            with open(f'enc.{filename}', 'wb') as file_encrypted:
                file_encrypted.write(file_contents_encrypted)
        except IOError as e:
            logging.error(e)
            return False
        
        print(f'Encryption Completed.Check your encrypted file: enc.{filename}')
        return True

    def run_decrypt(self, filename):

        try:
            with open(filename, 'rb') as file:
                data_plaintext = file.read()
        except IOError as e:
            logging.error(e)
            return False

        response = self.kms_client.decrypt(
            CiphertextBlob=data_plaintext,
            KeyId=self.key_id
        )
        file_contents_decrypted = response['Plaintext']
        try:
            with open(f'dec.{filename}', 'wb') as file_decrypted:
                file_decrypted.write(file_contents_decrypted)
        except IOError as e:
            logging.error(e)
            return False

        print(f'Decryption Completed. Check your encrypted file: dec.{filename}')
        return True


if __name__ == '__main__':
    KMSTasks()
