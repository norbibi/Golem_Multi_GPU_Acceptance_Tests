import requests
import json
import sys
import time
import signal
import os

gw_base_url = 'http://localhost:8000'

gw_get_proposals_url 	= gw_base_url + "/get-proposals"
gw_create_cluster_url 	= gw_base_url + "/create-cluster"
gw_get_cluster_url 		= gw_base_url + "/get-cluster"
gw_delete_cluster_url 	= gw_base_url + "/delete-cluster"
gw_create_node_url 		= gw_base_url + "/create-node"
gw_get_node_url 		= gw_base_url + "/get-node"
gw_delete_node_url 		= gw_base_url + "/delete-node"

#############################################################################

class PostResponse:
	def __init__(self, code, value):
		self.code = code
		self.value = value

	def pretty_print(self):
		try:
			print(json.dumps(self.value, indent=2))
		except:
			print(self.value)


def send_post_request(url, app_json, headers=None):
	try:
		req_res = requests.post(url, headers=headers, json=app_json)
		return PostResponse(req_res.status_code, json.loads(req_res.text))
	except:
		return PostResponse(500, {"detail": "None"})


def json_pretty_print(my_json):
	print(json.dumps(my_json, indent=2))

#############################################################################

def send_request_get_proposals(json_market_config):
	return send_post_request(gw_get_proposals_url, json_market_config)

def send_request_create_cluster(json_cluster_config):
	return send_post_request(gw_create_cluster_url, json_cluster_config)

def send_request_get_cluster(json_cluster_id):
	return send_post_request(gw_get_cluster_url, json_cluster_id)

def send_request_delete_cluster(json_cluster_id):
	return send_post_request(gw_delete_cluster_url, json_cluster_id)

def send_request_create_node(json_node_config):
	return send_post_request(gw_create_node_url, json_node_config)

def send_request_get_node(json_node_id):
	return send_post_request(gw_get_node_url, json_node_id)

def send_request_delete_node(json_node_id):
	return send_post_request(gw_delete_node_url, json_node_id)

#############################################################################

def get_json_market_config(subnet_tag, min_mem_gib, min_storage_gib, min_gpu_quantity):
	return {
		"market_config": {
		    "demand": {
		      	"payloads": [
			        {
			          	"golem_workers.payloads.ClusterNodePayload": {
			            	"runtime": "vm-nvidia",
			            	"subnet_tag": subnet_tag,
			            	"min_mem_gib": min_mem_gib,
			            	"min_storage_gib": min_storage_gib,
			            	"outbound_urls": [
			              		"https://huggingface.co",
			              		"https://cdn-lfs.huggingface.co",
			              		"https://cdn-lfs-us-1.huggingface.co",
			              		"https://gpu-provider.dev.golem.network"
			            	]
			          	}
			        }
		      	],
		      	"constraints": [
		        	f"golem.!exp.gap-35.v1.inf.gpu.d0.quantity>={min_gpu_quantity}"
		      	]
		    }
		}
	}

def get_json_cluster_config(cluster_id, average_duration_hours, average_max_cost, payment_network):
	return {
		"cluster_id": cluster_id,
		"budget_types": {
			"default": {
				"budget": {
					"golem_workers.budgets.AveragePerCpuUsageLinearModelBudget": {
						"average_cpu_load": 1,
						"average_duration_hours": average_duration_hours,
						"average_max_cost": average_max_cost
					}
				},
				"scope": "cluster"
			}
		},
		"network_types": {
			"default": {
				"ip": "192.168.0.1/16"
			}
		},
		"node_types": {
			"default": {
				"market_config": {
					"filters": [
						{
							"golem_reputation.ProviderBlacklistPlugin": {
								"payment_network": payment_network
							}
						}
					],
					"sorters": [
						{
							"golem_reputation.ReputationScorer": {
								"payment_network": payment_network
							}
						}
					]
				},
				"on_stop_commands": [
					"golem_workers.work.stop_activity"
				]
			}
		}
	}

def get_json_cluster_id(cluster_id):
	return {
		"cluster_id": cluster_id
	}

def get_json_node_config_vllm_multigpu(cluster_id, subnet_tag, min_gpu_quantity, deploy_timeout_minutes, model_repo_name, huggingface_auth_token, tensor_parallel_size):
	return {
		"cluster_id": cluster_id,
		"node_networks": {
			"default": {}
		},
		"node_config": {
			"market_config": {
				"demand": {
					"payloads": [
						{
							"golem_workers.payloads.ClusterNodePayload": {
								"runtime": "vm-nvidia",
								"image_tag": "maugnorbert/vllm_multigpu:11",
								"subnet_tag": subnet_tag,
								"min_mem_gib": min_mem_gib,
			            		"min_storage_gib": min_storage_gib,
			            		"outbound_urls": [
			              			"https://huggingface.co",
			              			"https://cdn-lfs.huggingface.co",
			              			"https://cdn-lfs-us-1.huggingface.co",
			              			"https://gpu-provider.dev.golem.network"
			            		]
							}
						}
					],
					"constraints": [
						f"golem.!exp.gap-35.v1.inf.gpu.d0.quantity>={min_gpu_quantity}"
					]
				}
			},
			"on_start_commands": [
				{
					"golem_workers.work.deploy_and_start_activity": {
						"deploy_timeout_minutes": deploy_timeout_minutes
					}
				},
				{
					"golem_workers.work.run_in_shell": [
						f"cd /workspace/ && HF_HUB_DOWNLOAD_TIMEOUT=600 ./start.sh --model_repo_name {model_repo_name} --huggingface_auth_token {huggingface_auth_token} --tensor_parallel_size {tensor_parallel_size} > /workspace/output/log 2>&1 &"
					]
				}
			],
			"sidecars": [
				{
					"golem_workers.sidecars.WebsocatPortTunnelSidecar": {
						"network_name": "default",
						"local_port": "8080",
						"remote_port": "8000"
					},
				},
				{
					"golem_workers.sidecars.WebsocatPortTunnelSidecar": {
						"network_name": "default",
						"local_port": "8081",
						"remote_port": "8001"
					}
				}
			]
		}
	}

def get_json_node_id(cluster_id, node_id):
	return {
		"cluster_id": cluster_id,
		"node_id": node_id
	}

#############################################################################

def get_proposals(subnet_tag, min_mem_gib, min_storage_gib, min_gpu_quantity):
	json_market_config = get_json_market_config(subnet_tag, min_mem_gib, min_storage_gib, min_gpu_quantity)
	proposals = send_request_get_proposals(json_market_config)
	if proposals.code != 200:
		print("Error retrieving proposals")
		proposals.pretty_print()
		return None
	number_provider_found = len(proposals.value['proposals'])
	if number_provider_found == 0:
		print("No provider found")
		return None
	else:
		return proposals.value['proposals']

def create_cluster(cluster_id, average_duration_hours, average_max_cost, payment_network):
	json_cluster_config = get_json_cluster_config(cluster_id, average_duration_hours, average_max_cost, payment_network)
	cluster = send_request_create_cluster(json_cluster_config)
	if cluster.code != 200:
		print("Error creating cluster")
		cluster.pretty_print()
		return None
	else:
		return cluster.value['cluster']

def delete_cluster(cluster_id):
	json_cluster_id = get_json_cluster_id(cluster_id);
	ret = send_request_delete_cluster(json_cluster_id)
	if ret.code != 200:
		print("Error deleting cluster")
		ret.pretty_print()
	else:
		return ret.value['cluster']

def create_node(json_node_config):
	node = send_request_create_node(json_node_config)
	if node.code != 200:
		print("Error creating node")
		node.pretty_print()
		return None
	else:
		return node.value['node']

def get_node(cluster_id, node_id):
	json_node_id = get_json_node_id(cluster_id, node_id)
	ret = send_request_get_node(json_node_id)
	if ret.code != 200:
		print("Error getting node")
		ret.pretty_print()
		return None
	else:
		return ret.value['node']

def delete_node(cluster_id, node_id):
	json_node_id = get_json_node_id(cluster_id, node_id)
	ret = send_request_delete_node(json_node_id)
	if ret.code != 200:
		print("Error deleting node")
		ret.pretty_print()
	else:
		return ret.value['node']

#############################################################################

def wait_node_ready(cluster_id, node_id):
	node = {}
	state = None
	while((node != None) and (state != "started") and (state != "stopped")):
		time.sleep(10)
		node = get_node(cluster_id, node_id)
		if node != None:
			state = node["state"]
		else:
			return None
	return state

def wait_model_ready(model):
	test_req = PostResponse(0, {"detail": "None"})
	while test_req.code != 200:
		test_req = test_vllm(model, "Who won the World Cup in 2022?")
		time.sleep(10)


def signal_handler(sig, frame):
	print("Exiting")
	delete_node(cluster_id, node_id)
	delete_cluster(cluster_id)
	sys.exit(0)

#############################################################################

def test_vllm(model, question):
	url = "http://localhost:8080/v1/chat/completions"
	headers = {
		"Accept": "application/json",
		"Content-Type": "application/json"
	}
	data = data={
		"model": model,
		"max_tokens": 300,
		"temperature": 0,
		"messages": [
			{"role": "system", "content": "You are a helpful assistant."},
			{"role": "user", "content": question},
		],
	}
	return send_post_request(url, data, headers)

##### Parameters ############################################################

subnet_tag = "gpu-test"
min_mem_gib = 32
min_storage_gib = 128
min_gpu_quantity = 4
deploy_timeout_minutes = 60

cluster_id = "example"
average_duration_hours = 1
average_max_cost = 2
payment_network = "holesky"

model = "casperhansen/llama-3-70b-instruct-awq"
huggingface_auth_token = os.environ['HF_TOKEN']

questions = [	"Who won the World Cup in 2022?"
				"Where are a dog's sweat glands located?"
				"Who narrates the adventures of Sherlock Holmes?"
				"Who was the fortieth president of the USA?"
				"What does Bistro mean in Russian?"
				"How many nautical miles are there in one degree of latitude?"
				"Who founded the French Academy?"
				"What is the longest river in Western Europe?"
				"Who is inseparable from Bonnie Parker?"
				"What is the northern slope of a valley called?"
				"Who is the Sun God in ancient Egypt?"
				"What is the name of the doctor in Cluedo?"
				"What is the capital of Bermuda?"
				"What was the first name of the game of bowls?"
				"Which being walks on 4 legs in the morning, 2 at lunchtime and 3 in the evening?"
				"How long does it take for the Earth to revolve around the Sun?"
				"In which country are Afrikaans and English spoken?"
				"Which city built the first metro?"
				"Who first set foot on the Moon?"
				"Which of the five senses does the snake lack?"
				"What does the penguin eat?"
				"What openings do fish and violins have in common?"
				"On which continent is Adélie Land located?"
				"What does a conchyophile collect?"
				"Where are the most expensive seats in a bullfight arena?"
				"Where was Wolfgang Amadeus Mozart born?"
				"Which people invented gunpowder?"
				"What are Rubens first names?"
				"Which river has the largest flow in the world?"
				"How many players are there on the field on a baseball team?"
				"What do you call a boat with three hulls?"
				"What does a seringueiro harvest in Brazil?"
				"Who is The Magnificent”?"
				"Who is the heroine of Notre-Dame de Paris?"
				"Which capital stands at the confluence of the Blue Nile and the White Nile?"
				"Who had tiny tootsies?"
				"On which side of the plate should the wine glass be placed?"
			]

#############################################################################

signal.signal(signal.SIGINT, signal_handler)

###### Verify if provider available(s) ######################################

proposals = get_proposals(subnet_tag, min_mem_gib, min_storage_gib, min_gpu_quantity)
if proposals is None:
	sys.exit()
else:
	print(f"Found {len(proposals)} provider(s)")

##### Create cluster ########################################################

cluster = create_cluster(cluster_id, average_duration_hours, average_max_cost, payment_network)
if cluster is None:
	sys.exit()
else:
	print(f"Cluster {cluster_id} created with success")

time.sleep(5)

##### Add node to cluster ###################################################

json_node_config = get_json_node_config_vllm_multigpu(cluster_id, subnet_tag, min_gpu_quantity, deploy_timeout_minutes, model, huggingface_auth_token, min_gpu_quantity)
node = create_node(json_node_config)
if node is not None:
	node_id = node['node_id']
	print(f"Node {node_id} created with success")
else:
	delete_cluster(cluster_id)
	sys.exit()

##### Wait node become ready ################################################

state = ""
while state != "started":
	state = wait_node_ready(cluster_id, node_id)
	if state is None or state == "stopped":
		if state is None:
			print("Error getting node")
		else:
			print("Error, unattend stopped state")
		delete_node(cluster_id, node_id)
		delete_cluster(cluster_id)
		sys.exit()
		
print(f"Node {node_id} is now ready")

#############################################################################

wait_model_ready(model)

#############################################################################

for question in questions:
	test_req = test_vllm(model, question)
	if test_req.code == 200:
		print(question)
		try:
			print(test_req.value['choices'][0]['message']['content'])
		except:
			test_req.pretty_print()
		print("\n")

##### Delete node from cluster ##############################################

delete_node(cluster_id, node_id)

##### Delete cluster ########################################################

delete_cluster(cluster_id)
