from google.cloud import pubsub_v1
import requests, json, time
from pprint import pprint
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

project_id = "sirui-sun-test-project"
topic_id = "sf-notifications-test"

publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)

# get this instance's name
url = "http://metadata.google.internal/computeMetadata/v1/instance/name"
mds_headers = {'Metadata-Flavor': 'Google'}
r = requests.get(url, headers=mds_headers)
instance_name = r.text

# get this instance's zone
url = "http://metadata.google.internal/computeMetadata/v1/instance/zone"
mds_headers = {'Metadata-Flavor': 'Google'}
r = requests.get(url, headers=mds_headers)
zone_name = r.text.split("/")[-1]

# publish maintenance status every 30s
while(True):

	# get maintenance notice from this instance's Metadata Server endpoint
	url = "http://metadata.google.internal/computeMetadata/v1/instance/upcoming-maintenance?alt=json"
	r = requests.get(url, headers=mds_headers)
	mds_maint_data = r.json()

	# get maintenance notice from this instance's API endpoint
	credentials = GoogleCredentials.get_application_default()
	service = discovery.build('compute', 'alpha', credentials=credentials)
	request = service.instances().get(project=project_id, zone=zone_name, instance=instance_name)
	response = request.execute()
	api_maint_data = {}
	if "upcomingMaintenance" in response:
		api_maint_data = response.upcomingMaintenance

	# send this all to pubsub
	data = {
		"instanceName": instance_name,
		"zone": zone_name,
		"mdsMaintenanceNotice": mds_maint_data,
		"apiMaintenanceData": api_maint_data
	}

	data = json.dumps(data).encode('utf-8')
	future = publisher.publish(topic_path, data)
	print(future.result())
	print("Published message.")

	time.sleep(30)