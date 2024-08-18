FROM maugnorbert/docker_golem_nvidia_555_58_ubuntu_20_04:latest AS base

RUN wget https://developer.download.nvidia.com/compute/cuda/12.4.1/local_installers/cuda_12.4.1_550.54.15_linux.run \
	&& sh cuda_12.4.1_550.54.15_linux.run --silent --toolkit \
	&& rm cuda_12.4.1_550.54.15_linux.run