# Requirement: pip3 install boto3 
# Requirement: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
# Usage: empty_delete_bucket.py -b <bucket_name>

from boto3 import resource, client 
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument(
    '-b',
    '--bucketname',
    help='Exemplo: script.py -b "bucketname"',
    required=True
    )
args = parser.parse_args()

s3 = resource('s3').Bucket(args.bucketname)
s3.objects.all().delete()

client('s3').delete_bucket(
    Bucket=args.bucketname
)
