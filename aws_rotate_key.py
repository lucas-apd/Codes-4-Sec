# Requirements: awscli, python3, boto3
# by github.com/Lucas-L-Alcantara
#.
#..
#...
# Script for rotate aws iam access key

import boto3
from boto3 import Session
import argparse
import time
import datetime
import os

#Variables
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help="Example: aws.manage.keys.py -u <username>", required=True)
args = parser.parse_args()
global iamuser
iamuser = args.username

key1_id = ''
key2_id = ''
total = 0
key1_age = " OLDER !"
key2_age = " NEWER !"
access_key = ''

curdate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
currentd = time.mktime(datetime.datetime.strptime(curdate, "%Y-%m-%d %H:%M:%S").timetuple())


def rotate_key(iamuser, access_key):
    a = ''

    while a != 'Y' or 'N':
        a = input("\nWARN! Confirm do rotate the key %s [Y/N]? " % access_key)
        a = str.capitalize(a)
        if a == 'Y':
            iam.delete_access_key(UserName=iamuser, AccessKeyId=access_key)
            access_key_metadata = iam.create_access_key(UserName=iamuser)['AccessKey']
            access_key = access_key_metadata['AccessKeyId']
            secret_key = access_key_metadata['SecretAccessKey']
            print ("\nNICE \o/ Your new access key is { %s } and your new secret key is { %s }\n" % (access_key, secret_key))
            set_key(access_key, secret_key)
            out()
        elif a == 'N': out()

def set_key (access_key, secret_key):
    s = ''
    while s != 'Y' or 'N':
        s = input("\nDo you want to configure current device to use your new key [Y/N]? ")
        s = str.capitalize(s)
        if s == 'Y':
            p = os.popen('aws configure set aws_access_key_id %s' % (access_key))
            print(p.read())
            p = os.popen('aws configure set aws_secret_access_key %s' % (secret_key))
            print(p.read())
            print ("\n\t Device configurated \o/ \n")
            out()
        elif s == 'N': out()

def out():
    print("\n Goodbye!! ;) \n")
    exit()

def choice_key(iamuser, access_key):

    print("\n------------------------- START -------------------------")
    print("\nYou are working with that key >> " + current_credentials.access_key + "\n")
    print("\tList of available keys for " + iamuser + ":\n")
    print("\t1. " + key1_id + " =" + key1_age + " ( Created " + str(since1) + " days ago. )")

    if total > 1:
        print("\t2. " + key2_id + " =" + key2_age + " ( Created " + str(since2) + " days ago. )")

    n = "1"

    while n != '1' or '2':
        if total > 1:
            n = input("\nWhich key you want to rotate? [1/2]? ")
        if n == '1':
            access_key=key1_id
            print("\n \t Account %s has only one key \n" % iamuser)
            rotate_key(iamuser, access_key)
        if n == '2':
            access_key=key2_id
            rotate_key(iamuser, access_key)



session = Session()
credentials = session.get_credentials()
current_credentials = credentials.get_frozen_credentials()
iam = boto3.client('iam')

keys = iam.list_access_keys(UserName= iamuser)

for key in keys['AccessKeyMetadata']:
        if key['Status']=='Inactive':
            total = total + 1
        if key['Status']=='Active':total = total + 1

key1_id = keys['AccessKeyMetadata'][0]['AccessKeyId']
key1_st = keys['AccessKeyMetadata'][0]['Status']
key1_dt = keys['AccessKeyMetadata'][0]['CreateDate']
key1_dt = key1_dt.strftime("%Y-%m-%d %H:%M:%S")
adate1 = time.mktime(datetime.datetime.strptime(key1_dt, "%Y-%m-%d %H:%M:%S").timetuple())
key1_days = (currentd - adate1)/60/60/24
since1 = (int(round(key1_days)))

access_key = key1_id

if total > 1:
    newkey = key2_id
    key2_id = keys['AccessKeyMetadata'][1]['AccessKeyId']
    key2_st = keys['AccessKeyMetadata'][1]['Status']
    key2_dt = keys['AccessKeyMetadata'][1]['CreateDate']
    key2_dt = key2_dt.strftime("%Y-%m-%d %H:%M:%S")
    adate2 = time.mktime(datetime.datetime.strptime(key2_dt, "%Y-%m-%d %H:%M:%S").timetuple())
    key2_days = (currentd - adate2)/60/60/24
    since2 = (int(round(key2_days)))

    if adate1 > adate2:

        key1_age = " NEWER !"
        key2_age = " OLDER !"

choice_key(iamuser, access_key)
