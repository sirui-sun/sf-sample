import requests, json, time
from pprint import pprint
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

# reads config file and creates VMs if they don't already exist
project_id = "sirui-sun-test-project"
config_file = open('config', 'r')
configs = config_file.readlines()[1:]

# check if the VM exists
def vmExists(zone, name):
	# get maintenance notice from this instance's API endpoint
	credentials = GoogleCredentials.get_application_default()
	service = discovery.build('compute', 'alpha', credentials=credentials)
	request = service.instances().get(project=project_id, zone=zone, instance=name)
	response = request.execute()
	pprint(response)

# Strips the newline character
for config in configs:
	config = config.strip().split(",")
	name = config[0]
	zone = config[1]
	machine_shape = config[2]
	gpu = config[3]
	ssd = config[4]

	print(vmExists(zone, name))