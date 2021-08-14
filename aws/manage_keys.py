# Requirements: awscli, python3, boto3
# by github.com/Lucas-L-Alcantara
#.
#..
#...
# Script for manage aws iam access keys

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

key1_days = ''
key2_days = ''
key1_id = ''
key2_id = ''
active =0
inactive = 0
total = 0
key1_age = "Older"
key2_age = "Newer"

curdate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
currentd = time.mktime(datetime.datetime.strptime(curdate, "%Y-%m-%d %H:%M:%S").timetuple())

def enable_key(dkey, iamuser):
    iam.update_access_key(UserName=iamuser, AccessKeyId=dkey, Status="Active")
    print (dkey + " has been Enabled.")
    choice_key(iamuser)

def create_key(iamuser):
    access_key_metadata = iam.create_access_key(UserName=iamuser)['AccessKey']
    access_key = access_key_metadata['AccessKeyId']
    secret_key = access_key_metadata['SecretAccessKey']
    print ("\nNICE \o/ Your new access key is { %s } and your new secret key is { %s }" % (access_key, secret_key) + "\n")
    set_key(access_key, secret_key)

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

def rotate_key(iamuser, access_key):
    a = ''

    while a != 'Y' or 'N':
        a = input("\nWARN! Confirm do rotate the key %s [Y/N]? " % access_key)
        a = str.capitalize(a)
        if a == 'Y':
            iam.delete_access_key(UserName=iamuser, AccessKeyId=oldkey)
            access_key_metadata = iam.create_access_key(UserName=iamuser)['AccessKey']
            access_key = access_key_metadata['AccessKeyId']
            secret_key = access_key_metadata['SecretAccessKey']
            print ("\nNICE \o/ Your new access key is { %s } and your new secret key is { %s }" % (access_key, secret_key) + "\n")
            set_key(access_key, secret_key)
            out()
        elif a == 'N': out()

def disable_key(access_key, iamuser):
    iam.update_access_key(UserName=iamuser, AccessKeyId=access_key, Status="Inactive")
    print ("\n Access Key " + access_key + " has been disabled.\n")
    choice_key()

def delete_key(access_key, iamuser):
    a = ''
    while a != 'Y' or 'N':
        a = input("\nWARN! Confirm to delete the key %s: [Y/N] " % access_key)
        a = str.capitalize(a)
        if a == 'Y':
            iam.delete_access_key(UserName=iamuser, AccessKeyId=access_key)
            print ("\n Access Key " + access_key + " has been deleted.")
            out()
        elif a == 'N': out()

def out():
    print("\n Goodbye!! ;) \n")
    exit()

def choice_key(iamuser):

    print("\n------------------------- START -------------------------")
    print("\nYou are working with that key >> " + current_credentials.access_key + "\n")
    print("\tList of available keys for " + iamuser + ":\n")
    print("\t1. " + key1_id + " (Status: " + key1_st + " - Created: " + str(key1_dt) + " - Days: " + str(since1) + " = " + key1_age + " )")

    if total > 1:
        print("\t2. " + key2_id + " (Status: " + key2_st + " - Created: " + str(key2_dt) + " - Days: " + str(since2) + " = " + key2_age + " )")

    n = total
    access_key = key1_id

    while n != '1' or '2':
        if total > 1:
            n = input("\nWhich key you want to work with [1/2]? ")
        if n == '1':
            access_key=key1_id

        if n == '2':
            access_key=key2_id

        c=''
        while c != 'E' or 'C' or 'R' or 'I' or 'E' or 'N':
                print(
                    "\n C = Create \
                    \n E = Enable \
                    \n I = Disable \
                    \n D = Delete \
                    \n R = Rotate (Delete the selected key and create a new one) \
                    \n S = Select key \
                    \n N = Nothing (exit)"
                )
                c = input("\nWhat do you want to do? ")
                c = str.capitalize(c)

                if c == 'S':
                    choice_key(iamuser)

                if c == 'E':
                    enable_key(access_key, iamuser)

                if c == 'I':
                    disable_key(access_key, iamuser)

                if c == 'C':
                    if total == 2:
                        print("\n %s has 2 active keys. You must delete a key before you can create another key." % iamuser)
                    else:
                        create_key(iamuser)

                if c == 'R':
                    rotate_key(iamuser, access_key)

                if c == 'D':
                    delete_key(access_key, iamuser)

                elif c == 'N': out()

session = Session()
credentials = session.get_credentials()
current_credentials = credentials.get_frozen_credentials()
iam = boto3.client('iam')

keys = iam.list_access_keys(UserName= iamuser)

for key in keys['AccessKeyMetadata']:
        if key['Status']=='Inactive':
            total = total + 1
            inactive = inactive + 1
            dkey = key['AccessKeyId']
        if key['Status']=='Active':total = total + 1

key1_id = keys['AccessKeyMetadata'][0]['AccessKeyId']
key1_st = keys['AccessKeyMetadata'][0]['Status']
key1_dt = keys['AccessKeyMetadata'][0]['CreateDate']
key1_dt = key1_dt.strftime("%Y-%m-%d %H:%M:%S")
adate1 = time.mktime(datetime.datetime.strptime(key1_dt, "%Y-%m-%d %H:%M:%S").timetuple())
key1_days = (currentd - adate1)/60/60/24
since1 = (int(round(key1_days)))

oldkey = key1_id

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
        oldkey = key2_id
        newkey = key1_id
        key1_age = "Newer"
        key2_age = "Older"

choice_key(iamuser)
