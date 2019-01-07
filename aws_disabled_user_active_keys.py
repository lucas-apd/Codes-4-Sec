# Requirements: awscli, python3, boto3
# by github.com/Lucas-L-Alcantara
#.
#..
#...
# Script for list disabled aws accounts with active access key

from __future__ import print_function
import io
import csv
import boto3
import time

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


iam = boto3.client('iam')
complete = False

while not complete:
    resp = iam.generate_credential_report()
    complete = resp['State'] == 'COMPLETE'
    time.sleep(1)

report = iam.get_credential_report()


if report['ReportFormat'] != 'text/csv':
    raise RuntimeError('Unknown Format {}'.format(report['ReportFormat']))

report_csv = io.StringIO(report['Content'].decode('utf-8'))
csv_reader = csv.DictReader(report_csv)
reader = list(csv_reader)

print("\n\t-----------------------------------------")
print(bcolors.FAIL + "\tDisabled accounts with active access key:" + bcolors.ENDC)
print("\t-----------------------------------------\n")

for row in reader:
    if (row['password_enabled'] == 'false' and (row['access_key_1_active'] == 'true' or row['access_key_2_active'] == 'true')):

        print("\t\t" + row['user'] )

print("\n\t-----------------------------------------\n")

print("\t-----------------------------------------\n")
