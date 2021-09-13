#!/usr/bin/env python

# -----------------------------------------------------------
# initial Stable Fleet test
# -----------------------------------------------------------

import googleapiclient.discovery
import json

# Configuration 
compute = googleapiclient.discovery.build('compute', 'alpha')
project = "sirui-sun-test-project"
zone = "us-east1-a"
region = "us-east1"
instances = ["stable-fleet-t4-notice-worker-%02d" %i for i in range(0,1)]
# instances = ["stable-fleet-p4-test-%02d" %i for i in range(1,2)]

# Check whether there are any to be done tasks
# If so, it should perform the tasks

# For each existing VM, check whether it has a maintenance notification upcoming
# If so: it should schedule a task for the weekend to restart the VM

def log(content):
	print(str(content))

def create_stable_fleet_instance(instance):
	body = {
	  "name": instance,
	  "machineType": "projects/sirui-sun-test-project/zones/{0}/machineTypes/n1-standard-32".format(zone),
	  "tags": {
	    "items": [
	      "http-server",
	      "https-server"
	    ]
	  },
	  "guestAccelerators": [
	    {
	      "acceleratorCount": 1,
	      "acceleratorType": "projects/sirui-sun-test-project/zones/{0}/acceleratorTypes/nvidia-tesla-t4".format(zone)
	    }
	  ],
	  "metadata": {
    	"items": [
      	  {
	        "key": "startup-script",
	        "value": "python3.7 /home/siruisun/sf-test/publisher.py"
          }
    	]
  	  },
	  "disks": [
	    {
	      "kind": "compute#attachedDisk",
	      "type": "PERSISTENT",
	      "boot": True,
	      "mode": "READ_WRITE",
	      "autoDelete": True,
	      "deviceName": instance,
	      "initializeParams": {
	        "sourceImage": "projects/sirui-sun-test-project/global/images/stable-fleet-notifications-worker-image",
	        "diskType": "projects/sirui-sun-test-project/zones/{0}/diskTypes/pd-balanced".format(zone),
	        "diskSizeGb": "10"
	      },
	      "diskEncryptionKey": {}
	    }
	  ],
	  "canIpForward": False,
	  "networkInterfaces": [
	    {
	      "kind": "compute#networkInterface",
	      "subnetwork": "projects/sirui-sun-test-project/regions/{0}/subnetworks/default".format(region),
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
	  "confidentialInstanceConfig": {
	    "enableConfidentialCompute": False
	  }
	}

	result = compute.instances().insert(
		project = project,
		zone = zone,
		body = body
	).execute()
	return result

def get_instance(compute, zone, instance):
    result = compute.instances().get(
      project=project, 
      zone=zone,
      instance=instance
    ).execute()
    return result

# Check whether there are N VMs. Create all uncreated VMs if not
for instance in instances:
	try:
		print(get_instance(compute, zone, instance)['scheduling'])
	except googleapiclient.errors.HttpError as httpErr:
		if ("404" in str(httpErr)): 
			print(create_stable_fleet_instance(instance))
	except Exception as e:
		log(e)

# check for whether there are any upcoming notifications on these instances

