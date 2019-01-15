
# Requirements: awscli, python3, boto3
# by github.com/Lucas-L-Alcantara
#.
#..
#...
# Script for list aws ec2 instances with public port

import boto3
import json
from collections import defaultdict
from prettytable import PrettyTable



x = PrettyTable()
x.field_names = ["Name", "ID", "SGs", "Private IP", "Public IP", "Public Ports"]


ec2r= boto3.resource('ec2')
session = boto3.Session()
ec2 = session.resource('ec2')
acc_name =   str(boto3.client('iam').list_account_aliases()['AccountAliases'][0])

running_instances = ec2r.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}])

ec2info = defaultdict()

for instance in running_instances:
	
	for tag in instance.tags:
		if 'Name'in tag['Key']:
			name = tag['Value']

		
	if instance.public_ip_address is not None:
		
		sgs=[]
		
		for i in range(len(instance.security_groups)):
			sg_id=instance.security_groups[i]['GroupId']
			sgs.append(sg_id)
		
			open_ports = []	

		sg = ec2.SecurityGroup(sg_id)

		for i in range(len(sg.ip_permissions)):
			to_port = ''
			ip_proto = ''
			if 'ToPort' in sg.ip_permissions[i]:
				to_port = sg.ip_permissions[i]['ToPort']
			if 'IpProtocol' in sg.ip_permissions[i]:
				ip_proto = sg.ip_permissions[i]['IpProtocol']
				if '-1' in ip_proto:
					ip_proto = 'All'
			for j in range(len(sg.ip_permissions[i]['IpRanges'])):
				cidr_ports = "%s" % (to_port)
	
				if sg.ip_permissions[i]['IpRanges'][j]['CidrIp'] == '0.0.0.0/0':

					if ip_proto != 'icmp':
						open_ports.append(cidr_ports)
	 
			
		for s in sgs:
			if len(open_ports):
					ports = (', '.join(str(p) for p in open_ports))
					x.add_row([name, instance.id, s, instance.private_ip_address ,instance.public_ip_address, ports])
        
print("\n------------------------------------------------")
print(" Public Instances from ", acc_name, " Account:")
print("------------------------------------------------\n")

print(x, "\n")
