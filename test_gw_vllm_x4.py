import os
import sys
from gw_vllm_x4 import *

##### Parameters ############################################################

subnet_tag = "gpu-test"
min_mem_gib = 32
min_storage_gib = 128
min_gpu_quantity = 4
deploy_timeout_minutes = 60

cluster_id = "example"
node_id = None
average_duration_hours = 1
average_max_cost = 2
payment_network = "holesky"
huggingface_auth_token = os.environ['HF_TOKEN']

#############################################################################

if len(sys.argv) != 2:
	usage()

model = sys.argv[1]

if model not in models_tested_with_succes.keys():
	usage()

#############################################################################

def signal_handler():
	print("Exiting")
	if node_id is not None:
		delete_node(cluster_id, node_id)
	delete_cluster(cluster_id)
	quit()

signal.signal(signal.SIGINT, signal_handler)

###### Verify if provider available(s) ######################################

proposals = get_proposals(subnet_tag, min_mem_gib, min_storage_gib, min_gpu_quantity)
if proposals is None:
	quit()
else:
	print(f"Found {len(proposals)} provider(s)")

##### Create cluster ########################################################

cluster = create_cluster(cluster_id, average_duration_hours, average_max_cost, payment_network)
if cluster is None:
	quit()
else:
	print(f"Cluster {cluster_id} created with success")

time.sleep(5)

##### Add node to cluster ###################################################

json_node_config = get_json_node_config_vllm_multigpu(cluster_id, subnet_tag, min_mem_gib, min_storage_gib, min_gpu_quantity, deploy_timeout_minutes, huggingface_auth_token, model)
node = create_node(json_node_config)
if node is not None:
	node_id = node['node_id']
	print(f"Node {node_id} created with success")
else:
	delete_cluster(cluster_id)
	quit()

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
		quit()
		
print(f"Node {node_id} is now ready\n")

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
