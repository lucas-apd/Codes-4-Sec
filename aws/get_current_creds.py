# Requirements: awscli, python3, boto3
# by github.com/Lucas-L-Alcantara
#.
#..
#...
# This script will return search for aws (cli) credentials (access & secret) currently configured on your system

session = Session()
credentials = session.get_credentials()
current_credentials = credentials.get_frozen_credentials()
print(f"Your Current Credential:\n Access: {current_credentials.access_key} \n Secret: {current_credentials.secret_key}")

