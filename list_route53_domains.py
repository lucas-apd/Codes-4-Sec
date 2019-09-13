import boto3

session = boto3.Session(profile_name='default')
client = session.client('route53')

#OR

#client = boto3.client('route53')

#OR

#client = boto3.client('route53',
#                      aws_access_key_id="AKEY",
#                      aws_secret_access_key="SKEY",
#                      region_name="us-east-1"
#                      )

domain_list=[]

r53records = client.list_hosted_zones()

for domains in r53records["HostedZones"]:
	D_ID = domains['Id']
	DOMAIN = client.list_resource_record_sets(HostedZoneId=D_ID)

	for RRS in DOMAIN['ResourceRecordSets']:
		host = RRS['Name'][:-1]
		if not host in domain_list:
			print(host)
			domain_list.append(host)
