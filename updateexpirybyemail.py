import boto3
import time
import os
import sys 

domain = sys.argv[1]
emailid = sys.argv[2]
cutoffdate = sys.argv[3]

ssm_file = open("cut_off_ssm.json")
ssm_json = ssm_file.read()

target_emailid = emailid

instance_ids = {
	"deltekdev":"i-04d0e953afe07b3a3",
	"costpoint":"i-0e82a12d1ef934425",
	"avitru":"i-0750c84a6f973550a",
        "dco":"i-0fe3ff3ff41c18b17",
	"flexplus":"i-0f2717bceb18eea6f",
	"globaloss":"i-04b225ae477c52288",
	"engdeltek":"i-0667aa10a44eafc7c",
}

target_domain = instance_ids[domain]

ssm_doc_name = 'cut_off_ssm'

if domain == "avitru":
    region_name = "us-west-2"
else:
    region_name = "us-east-1"

ssm_client = boto3.client('ssm', region_name=region_name)

ssm_create_response = ssm_client.create_document(Content = ssm_json, Name = ssm_doc_name, DocumentType = 'Command', DocumentFormat = 'JSON', TargetType =  "/AWS::EC2::Instance")

ssm_run_response = ssm_client.send_command(InstanceIds = [target_domain], DocumentName=ssm_doc_name, DocumentVersion="$DEFAULT", TimeoutSeconds=120,  Parameters={'EmailID':[target_emailid],'Cutoffdate':[cutoffdate]})
print(f'{ssm_run_response}\n')
cmd_id = ssm_run_response['Command']['CommandId']

time.sleep(5)
ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_domain)
while ssm_status_response['StatusDetails'] == 'InProgress':
	time.sleep(5)
	ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_domain)

if ssm_status_response['StatusDetails'] == 'Success':
	print(f'User {target_emailid} account expiration update to {cutoffdate} has been triggered on {target_domain}\n')

cmd_output = ssm_status_response.get('StandardOutputContent','')
print(f'{cmd_output}\n')

with open('cutoffdate_logs.txt', 'w') as outfile:
	outfile.write(cmd_output)

ssm_delete_response = ssm_client.delete_document(Name=ssm_doc_name)
