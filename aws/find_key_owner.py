# Requirements: awscli (configurated), python3, boto3, argparse + aws iam permission
# by github.com/Lucas-L-Alcantara
#.
#..
#...
# This script will search for access key owner specified

import boto3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key", help="Example: aws_find_key_owner.py -k <key_id>", required=True)
args = parser.parse_args()

TARGET_KEY = args.key

resource = boto3.resource('iam')
client = boto3.client("iam")

print ("Searching for access key Owner. Please, Wait ...")

def find_key():
    for user in resource.users.all():
        list = client.list_access_keys(UserName=user.user_name)

        for key in user.access_keys.all():
            AccessId = key.access_key_id
            Status = key.status
            if AccessId == TARGET_KEY:
                print ("Key Owner is " + user.user_name + " and Key Status is " + Status)
                exit()
                return True
    return False

if not find_key():
print ('Sorry. Did not find access key ' + TARGET_KEY + ' in IAM users')
