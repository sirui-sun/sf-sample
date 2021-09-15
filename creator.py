import requests, json, time
from pprint import pprint
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
project_id = "sirui-sun-test-project"

# check if the VM exists
def vmExists(zone, name):
	try:
		credentials = GoogleCredentials.get_application_default()
		service = discovery.build('compute', 'alpha', credentials=credentials)
		request = service.instances().get(project=project_id, zone=zone, instance=name)
		response = request.execute()
		return True
	except HttpError as err:
		if err.resp.status == 404:
			return False
		else: raise


# create a VM instance with periodic maintenance intervals
def createPeriodicMaintenanceVM(name, zone, machine_shape, gpu, lssd):
	credentials = GoogleCredentials.get_application_default()
	service = discovery.build('compute', 'alpha', credentials=credentials)
	region = str.join("-", zone.split("-")[:-1])
	body = {
	  "name": name,
	  "machineType": "projects/{0}/zones/{1}/machineTypes/{2}".format(project_id, zone, machine_shape),
	  "guestAccelerators": [],
	  "disks": [
	    {
	      "kind": "compute#attachedDisk",
	      "type": "PERSISTENT",
	      "boot": True,
	      "mode": "READ_WRITE",
	      "autoDelete": True,
	      "deviceName": name,
	      "initializeParams": {
	        "sourceImage": "projects/sirui-sun-test-project/global/images/sf-worker",
	        "diskType": "projects/{0}/zones/{1}/diskTypes/pd-balanced".format(project_id, zone),
	        "diskSizeGb": "10"
	      },
	      "diskEncryptionKey": {}
	    }
	  ],
	  "canIpForward": False,
	  "networkInterfaces": [
	    {
	      "kind": "compute#networkInterface",
	      "subnetwork": "projects/{0}/regions/{1}/subnetworks/default".format(project_id, region),
	      "accessConfigs": [
	        {
	          "kind": "compute#accessConfig",
	          "name": "External NAT",
	          "type": "ONE_TO_ONE_NAT",
	          "networkTier": "PREMIUM"
	        }
	      ],
	      "aliasIpRanges": []
	    }
	  ],
	  "description": "",
	  "labels": {
	  	"stable-fleet-test": ""
	  },
	  "scheduling": {
	    "preemptible": False,
	    "onHostMaintenance": "TERMINATE",
	    "automaticRestart": True,
	    "maintenanceInterval": "PERIODIC",
	    "nodeAffinities": []
	  },
	  "deletionProtection": False,
	  "reservationAffinity": {
	    "consumeReservationType": "ANY_RESERVATION"
	  },
	  "serviceAccounts": [
	    {
	      "email": "806547283812-compute@developer.gserviceaccount.com",
	      "scopes": [
	        "https://www.googleapis.com/auth/cloud-platform"
	      ]
	    }
	  ],
	  "shieldedInstanceConfig": {
	    "enableSecureBoot": False,
	    "enableVtpm": True,
	    "enableIntegrityMonitoring": True
	  },
	}

	# TODO: allow configuration by # of GPUs
	if(gpu != "none"):
		body.guestAccelerators = [
	    	{
	      		"acceleratorCount": 1,
	      		"acceleratorType": "projects/{0}/zones/{1}/acceleratorTypes/{2}".format(project_id,zone,gpu)
	    	}
		]

	# TODO: allow configuration by # of lssds
	if(lssd != "none"):
		lssd_body = {
			"autoDelete": true,
			"deviceName": "local-ssd-0",
			"initializeParams": {
				"diskType": "projects/{0}/zones/{1}/diskTypes/local-ssd".format(project_id,zone)
			},
			"interface": "NVME",
			"mode": "READ_WRITE",
			"type": "SCRATCH"
		}
		body.disks.append(lssd_body)

	request = service.instances().insert(project=project, zone=zone, body=body)
	request.execute()
	print("created {0}".format(name))

# reads config file and creates VMs if they don't already exist
config_file = open('config', 'r')
configs = config_file.readlines()[1:]

# Strips the newline character
for config in configs:
	config = config.strip().split(",")
	name = config[0]
	zone = config[1]
	machine_shape = config[2]
	gpu = config[3]
	lssd = config[4]

	if(vmExists(zone, name)):
		print("skipping {0}: VM instances exists".format(name)
	else:
		createPeriodicMaintenanceVM(name, zone, machine_shape, gpu, lssd)


