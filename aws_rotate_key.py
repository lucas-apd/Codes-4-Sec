# Requirements: awscli, python3, boto3
# by github.com/Lucas-L-Alcantara
#.
#..
#...
# Script for rotate aws iam access key
from boto3 import Session
from boto3 import client
from argparse import ArgumentParser
from datetime import datetime
from os import popen


def get_keys(iamuser):

    all_keys = []
    try:
        session = Session()
        credentials = session.get_credentials()
        credentials = credentials.get_frozen_credentials()
        print(f"\nAccess em uso: {credentials.access_key}")
        iam = client('iam')
        keys = iam.list_access_keys(UserName=iamuser)

    except:
        print("Não foi possível conectar à AWS.")
        exit()

    for key in keys['AccessKeyMetadata']:
        user_key = {}
        if key['Status'] == 'Active':
            user_key['Id']=key['AccessKeyId']
            user_key['days'] = (datetime.now(key['CreateDate'].tzinfo) - key['CreateDate']).days

            if int(user_key['days']) > 180:
                print("\n Eita porra! Essa já poderia ser rotacionada em? \n"
                      f" \n\tAccess ID: {user_key['Id']} \t Idade (dias): {user_key['days']}")
                rotate_key(iamuser, str(key['AccessKeyId']))

        all_keys.append(user_key)

    print(f"\nSuas chaves atuais: \n\t{all_keys}")

def rotate_key(iamuser, access_key):
    a = ''
    iam = client('iam')
    while a != 'Y' or 'N':
        a = input("\n\tQuer rotacionar agora? [Y/N]? ")
        a = str.capitalize(a)
        if a == 'Y':
            iam.delete_access_key(UserName=iamuser, AccessKeyId=access_key)
            access_key_metadata = iam.create_access_key(UserName=iamuser)['AccessKey']
            access_key = access_key_metadata['AccessKeyId']
            secret_key = access_key_metadata['SecretAccessKey']
            print (f"\n \o/\o/\o/ Sua nova access: {access_key} e secret key: {secret_key}\n")
            set_key(access_key, secret_key)
            break
        elif a == 'N': break

def set_key (access_key, secret_key):
    s = ''
    while s != 'Y' or 'N':
        s = input("\nQuer configurar a nova chave neste dispositivo? [Y/N]? ")
        s = str.capitalize(s)
        if s == 'Y':
            p = popen('aws configure set aws_access_key_id %s' % (access_key))
            print(p.read())
            p = popen('aws configure set aws_secret_access_key %s' % (secret_key))
            print(p.read())
            print ("\n\t Uhuuuu! Dispositivo configurado \o/ \n")
            break
        elif s == 'N': break

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-u", "--username", help="Example: aws.manage.keys.py -u <username>", required=True)
    args = parser.parse_args()
    iamuser = args.username

    get_keys(iamuser)
