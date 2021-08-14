from argparse import ArgumentParser
from boto3 import Session
from botocore.exceptions import ClientError


def get_aws_regions(profile):

    session = Session(profile_name=profile)
    return session.get_available_regions('rds')

def get_not_encrypted_rds(profile, regions):

    dec_rds_by_region = {}

    for region in regions:   
        decypted_rds_list = get_region_rds_info(profile, region)
        if decypted_rds_list:
            dec_rds_by_region[region] = decypted_rds_list

    for region in dec_rds_by_region:
        print(f'\nRegion {region} has {len(dec_rds_by_region[region])} not ecrypted RDS: \n {{}}'.format("\n".join(dec_rds_by_region[region])))

def get_region_rds_info(profile, region):
    try:
        session = Session(profile_name=profile, region_name=region)
        client = session.client('rds')
        regions_rds = client.describe_db_instances()
    except ClientError as error:
        return None
    
    if regions_rds:
        not_encrypted_rds_list =  [instance['DBInstanceIdentifier'] for instance in regions_rds['DBInstances'] if not instance['StorageEncrypted']]
    
    return not_encrypted_rds_list

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

    get_not_encrypted_rds(profile,get_aws_regions(profile))
