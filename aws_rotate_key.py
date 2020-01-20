# Requirements: awscli, python3, boto3, argparse.
#.
#..
#...
# Script for rotate aws access/secret key
# by github.com/Lucas-L-Alcantara

from boto3 import Session
from boto3 import client
from argparse import ArgumentParser
from datetime import datetime
from os import popen

DAYS_THRESHOLD = 180

def get_keys(iamuser):
    all_keys = []
    try:
        session = Session()
        credentials = session.get_credentials()
        credentials = credentials.get_frozen_credentials()
        print(f"\nAccess em uso: {credentials.access_key}")
        iam = client('iam')
        keys = iam.list_access_keys(UserName=iamuser)
    except Exception as e:
        print('Não foi possível conectar à AWS.')
        print('Erro:', e)
        exit()
        
    for key in keys['AccessKeyMetadata']:
        user_key = {}
        
        if key['Status'] != 'Active':
            continue
            
        user_key['Id']=key['AccessKeyId']
        user_key['days'] = (datetime.now(key['CreateDate'].tzinfo) - key['CreateDate']).days
        
        new_access_key = None

        if int(user_key['days']) >= DAYS_THRESHOLD:
            print('\n Eita porra! Essa já poderia ser rotacionada, hein? \n'
                  f" \n\tAccess ID: {user_key['Id']} \t Idade (dias): {user_key['days']}")
            new_access_key = rotate_key(iamuser, str(key['AccessKeyId']))
            if new_access_key:
                user_key['Id'] = new_access_key
                user_key['days'] = 0

        all_keys.append(user_key)

    print(f'\nSuas chaves atuais:')
    for i in all_keys:
        print('\tID:', i['Id'], '\tDias:', i['days'])

def rotate_key(iamuser, access_key):
    a = ''
    iam = client('iam')
    while a not in {'Y', 'N'}:
        a = input('\n\tQuer rotacionar agora? [Y/N]? ')
        a = a.strip().upper()
        if a == 'Y':
            iam.delete_access_key(UserName=iamuser, AccessKeyId=access_key)
            access_key_metadata = iam.create_access_key(UserName=iamuser)['AccessKey']
            access_key = access_key_metadata['AccessKeyId']
            secret_key = access_key_metadata['SecretAccessKey']
            print(f'\n \o/\o/\o/ Sua nova access: {access_key} e secret key: {secret_key}\n')
            set_key(access_key, secret_key)
            return access_key
        elif a == 'N':
            return None

def set_key (access_key, secret_key):
    s = ''
    while s not in {'Y', 'N'}:
        s = input('\nQuer configurar a nova chave neste dispositivo? [Y/N]? ')
        s = s.strip().upper()
        if s == 'Y':
            p = popen(f'aws configure set aws_access_key_id {access_key}')
            print(p.read())

            p = popen(f'aws configure set aws_secret_access_key {secret_key}')
            print(p.read())

            print('\n\t Uhuuuu! Dispositivo configurado \o/ \n')
            break
        elif s == 'N':
            break


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-u', '--username', help='Example: aws.manage.keys.py -u <username>', required=True)

    args = parser.parse_args()
    iamuser = args.username

    get_keys(iamuser)
