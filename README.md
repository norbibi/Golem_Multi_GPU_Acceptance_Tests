# Golem Multi-GPU Acceptance

The purpose of this repo is to validate the multi-GPU runtime (beta) of Golem providers.  
  
One of the goals of multi-GPU is to use the VLLM framework in order to be able to do inference on LLM models larger than the VRAM of a single GPU.  
  
This is what we propose to do with for example the casperhansen/llama-3-70b-instruct-awq model using a provider equipped with 4x 24GB GPUs.  
  
We will use the python package golem-workers which is an OpenAPI compatible REST API for managing clusters of Golem providers.  

**Create GVMI VLLM v0.5.4**  
  
The creation of the image is done in 2 steps:  
- creation of an ubuntu 20.04 image with the NVIDIA 550 driver and CUDA 12.4 (on which VLLM v0.5.4 is based)  
  I broke this step into 2 because not all GPU applications need CUDA.  
  These steps are optional, images are available on DockerHub.  
  ``` 
  cd docker_golem_nvidia_555_58_ubuntu_20_04
  docker build -t maugnorbert/docker_golem_nvidia_555_58_ubuntu_20_04 .
  ```
  and
  ```
  cd docker_golem_cuda_12_4_1_nvidia_555_58_ubuntu_20_04
  docker build -t maugnorbert/docker_golem_cuda_12_4_1_nvidia_555_58_ubuntu_20_04 .
  ``` 

- Installation and build of VLLM on this image (including customization for use on Golem)  
  This image has already been built and pushed to the Golem registry under the tag maugnorbert/vllm_multigpu:11  
  ``` 
  cd docker_golem_vllm_multigpu
  git clone --depth 1 --branch v0.5.4 https://github.com/vllm-project/vllm.git
  DOCKER_BUILDKIT=1 docker build --tag maugnorbert/vllm_multigpu:11 .
  ```

**Install and run Golem-Worker Webserver**  
  
1. Install golem-workers via:
   ```
   pip install golem-workers
   ```
   This step should install `yagna` binary for the next steps.
2. Start `golem-node` instance. This will occupy your terminal session, so it's best to do it in separate session.
   ```
   yagna service start
   ```
3. Prepare some funds for Golem's free test network. 
   Note that this step is needed mostly once per `golem-node` installation. 
   ```
   yagna payment fund
   ```
4. Create new `golem-node` application token
   ```
   yagna app-key create <your-token-name>
   ```
   and put generated app-key into the `.env` file in the current directory
   ```
   YAGNA_APPKEY=<your-application-token>
   ```
5. If you want to use Golem Reputation put new entry in `.env` file in the current directory
   ```
   GLOBAL_CONTEXTS=["golem_reputation.ReputationService"]
   ```
6. Start golem-workers web server instance
   ```
   uvicorn golem_workers.entrypoints.web.main:app
   ```


**Run test**  

The simple python test script test_gw_vllm_x4.py uses the Golem-workers library to create a cluster, add a multi-GPU provider node, launch the VLLM server on it and execute our inference queries. 
``` 
python3 test_gw_vllm_x4.py
```
