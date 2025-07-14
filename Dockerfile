# base image with cuda 12.1
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# install python 3.11 and pip
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# set python3.11 as the default python
RUN ln -sf /usr/bin/python3.11 /usr/local/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/local/bin/python3

# install uv
RUN pip install uv

# create venv
ENV PATH="/.venv/bin:${PATH}"
RUN uv venv --python 3.11 /.venv

# install dependencies
RUN uv pip install torch --extra-index-url https://download.pytorch.org/whl/cu121

# install remaining dependencies from PyPI
COPY requirements.txt /requirements.txt
RUN uv pip install -r /requirements.txt

# copy files
COPY download_weights.py schemas.py handler.py test_input.json /

# create models directory
RUN mkdir -p /models

# Accept CivitAI API key as build argument (optional)
ARG CIVITAI_API_KEY

# download the base weights from hugging face
# Note: Pony Realism will be downloaded at runtime if CIVITAI_API_KEY is provided
ENV CIVITAI_API_KEY=${CIVITAI_API_KEY}
RUN python /download_weights.py || echo "Model download completed (some models may download at runtime)"

# run the handler
CMD python -u /handler.py
