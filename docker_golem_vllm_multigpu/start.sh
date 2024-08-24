#! /bin/bash

EVENTS_FILE_PATH="/workspace/output/events.log"
MAINTENANCE_SERVER_PORT=8001

log_current_time() {
  current_time=`dig @8.8.8.8 huggingface.co | grep -oP "^;; WHEN: \K.*"`
  if [[ "$current_time" ]]; then
    echo "$1,$current_time" >> $EVENTS_FILE_PATH
  fi
}

wait_for_service_ready() {
  while ! curl -s http://localhost:"$1" > /dev/null
  do
      sleep 0.5
  done
  log_current_time "service_ready_at"
}

log_current_time "provisioned_at"
echo "Container started"

wait_for_service_ready "8000/health" &

python3 maintenance_server.py --events_file $EVENTS_FILE_PATH --port $MAINTENANCE_SERVER_PORT &

PARSED_OPTIONS=$(getopt -o '' --long model_repo_name:,startup_script_url:,huggingface_auth_token:,tensor_parallel_size: -- "$@" )
model_repo_name="" startup_script_url="" huggingface_auth_token="" tensor_parallel_size="" max_model_len="" gpu_memory_utilization="" max_num_seqs="" enforce_eager="" revision=""

while true; do
  case "$1" in
    --model_repo_name) model_repo_name=$2; shift 2;;
    --startup_script_url) startup_script_url=$2; shift 2;;
    --huggingface_auth_token) huggingface_auth_token=$2; shift 2;;
    --tensor_parallel_size) tensor_parallel_size=$2; shift 2;;
    --max_model_len) max_model_len=$2; shift 2;;
    --gpu_memory_utilization) gpu_memory_utilization=$2; shift 2;;
    --max_num_seqs) max_num_seqs=$2; shift 2;;
    --enforce_eager) enforce_eager=$2; shift 2;;
    --revision) enforce_eager=$2; shift 2;;
    *) break;;
esac
done

if [[ -z "${model_repo_name}" ]]; then
  echo "--model_repo_name cannot be empty!"
  exit 1
fi

if [[ $huggingface_auth_token ]]; then
  export HF_TOKEN=$huggingface_auth_token
fi

if [[ -z "${tensor_parallel_size}" ]]; then
  tensor_parallel_size=1
fi

if [[ $startup_script_url ]]
then
    cd /workspace/
    script_name=$(basename -- "$startup_script_url")

    if [[ $huggingface_auth_token ]]
    then
      curl -L -s --remote-name --remote-header-name -H "Authorization: Bearer ${huggingface_auth_token}" "$startup_script_url"
    else
      curl -L -s --remote-name --remote-header-name "$startup_script_url"
    fi

    if [ $? -eq 0 ]; then
      chmod a+x "$script_name"
      ./"$script_name"
    else
      echo "Error downloading startup script."
      exit 1
    fi
fi

echo "Checking CUDA..."
nvidia-smi 2>&1 | tee /workspace/output/nvidia-smi.log

echo "Starting service..."
cd /workspace/

cmd="python3 -m vllm.entrypoints.openai.api_server --host 0.0.0.0 --port 8000 --model $model_repo_name --tensor-parallel-size $tensor_parallel_size --download-dir /workspace/models"

if [[ ! -z "${max_model_len}" ]]; then
  cmd+=" --max-model-len $max_model_len"
fi

if [[ ! -z "${gpu_memory_utilization}" ]]; then
  cmd+=" --gpu-memory-utilization $gpu_memory_utilization"
fi

if [[ ! -z "${max_num_seqs}" ]]; then
  cmd+=" --max-num-seqs $max_num_seqs"
fi

if [[ ! -z "${enforce_eager}" ]]; then
  cmd+=" --enforce_eager"
fi

if [[ ! -z "${revision}" ]]; then
  cmd+=" --revision $revision"
fi

$cmd 2>&1 | tee /workspace/output/output.log
