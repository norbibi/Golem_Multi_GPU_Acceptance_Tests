import requests
import json
import time
import signal

from models_and_questions import *

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

def get_json_node_config_vllm_multigpu(cluster_id, subnet_tag, min_mem_gib, min_storage_gib, min_gpu_quantity, deploy_timeout_minutes, huggingface_auth_token, model_repo_name):
	model_params = models_tested_with_succes[model_repo_name]
	add_params = ""
	for key, value in model_params.items():
		 add_params += f" --{key} {value}"

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
								"image_tag": "maugnorbert/vllm_multigpu:17",
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
					"golem_workers.work.prepare_and_run_ssh_server": {
						"ssh_private_key_path": "/tmp/ssh_key"
					}
				},
				{
					"golem_workers.work.run_in_shell": [
						f"cd /workspace/ && HF_HUB_DOWNLOAD_TIMEOUT=60 ./start.sh --model_repo_name {model_repo_name} --huggingface_auth_token {huggingface_auth_token} {add_params} > /workspace/output/log 2>&1 &"
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
			{"role": "user", "content": question},
		],
	}
	return send_post_request(url, data, headers)