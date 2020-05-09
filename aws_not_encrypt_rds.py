from argparse import ArgumentParser
from boto3 import Session
from dataclasses import dataclass
from botocore.exceptions import ClientError


@dataclass
class RDSCounter:

    encrypted_db: int = 0
    not_encrypted_db: int = 0

    def add_encrypted_db(self):
        self.encrypted_db += 1

    def add_not_encrypted_db(self):
        self.not_encrypted_db += 1

    def get_encrypted_db(self):
        return self.encrypted_db

    def get_not_encrypted_db(self):
        return self.not_encrypted_db

    def get_total_db(self):
        return self.encrypted_db + self.not_encrypted_db


def get_region(profile):

    total_enc = 0
    total_dec = 0

    session = Session(profile_name=profile)
    acc_name = session.client('iam').list_account_aliases()[
        'AccountAliases'][0]
    #print('\n Account:', acc_name, '\n')

    regions = session.get_available_regions('rds')

    rds_dec = {}

    for region in regions:
        try:
            session = Session(profile_name=profile, region_name=region)
            client = session.client('rds')
            response = client.describe_db_instances()
            rds_counter, rds_list = get_region_rds(response)

            if rds_counter.get_total_db() > 0:
                rds_dec[region] = rds_list
                #print(rds_counter.get_not_encrypted_db(), ' not encrypted dbs in', region , f"\n{rds_list}\n")

            total_enc = total_enc + rds_counter.get_encrypted_db()
            total_dec = total_dec + rds_counter.get_not_encrypted_db()

        except ClientError as error:
            pass

    rds_dec['Total'] = f"{total_dec}/{total_enc+total_dec}"
    print(f"Decrypted DBs by Region:\n {rds_dec}")


def get_region_rds(response):
    notenc = []
    rds_counter = RDSCounter()

    for instance in response['DBInstances']:

        db_instance_name = instance['DBInstanceIdentifier']
        db_encrypt = instance['StorageEncrypted']

        if db_encrypt:
            rds_counter.add_encrypted_db()
        else:
            rds_counter.add_not_encrypted_db()
            notenc.append(db_instance_name)

    return rds_counter, notenc


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument(
        '-p',
        '--profile',
        help='Example: script.py -p <aws_cli_profile>',
        required=False
    )
    args = parser.parse_args()

    if not args.profile:
        profile = 'default'
    else:
        profile = args.profile

    get_region(profile)
