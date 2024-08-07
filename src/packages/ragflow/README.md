<div align="center">
<a href="https://demo.ragflow.io/">
<img src="web/src/assets/logo-with-text.png" width="520" alt="ragflow logo">
</a>
</div>

<p align="center">
  <a href="./README.md">English</a> |
  <a href="./README_zh.md">简体中文</a> |
  <a href="./README_ja.md">日本語</a>
</p>

<p align="center">
    <a href="https://github.com/infiniflow/ragflow/releases/latest">
        <img src="https://img.shields.io/github/v/release/infiniflow/ragflow?color=blue&label=Latest%20Release" alt="Latest Release">
    </a>
    <a href="https://demo.ragflow.io" target="_blank">
        <img alt="Static Badge" src="https://img.shields.io/badge/Online-Demo-4e6b99"></a>
    <a href="https://hub.docker.com/r/infiniflow/ragflow" target="_blank">
        <img src="https://img.shields.io/badge/docker_pull-ragflow:v0.7.0-brightgreen" alt="docker pull infiniflow/ragflow:v0.7.0"></a>
    <a href="https://github.com/infiniflow/ragflow/blob/main/LICENSE">
    <img height="21" src="https://img.shields.io/badge/License-Apache--2.0-ffffff?style=flat-square&labelColor=d4eaf7&color=2e6cc4" alt="license">
  </a>
</p>

<details open>
<summary></b>📕 Table of Contents</b></summary>
  
- 💡 [What is RAGFlow?](#-what-is-ragflow)
- 🎮 [Demo](#-demo)
- 📌 [Latest Updates](#-latest-updates)
- 🌟 [Key Features](#-key-features)
- 🔎 [System Architecture](#-system-architecture)
- 🎬 [Get Started](#-get-started)
- 🔧 [Configurations](#-configurations)
- 🛠️ [Build from source](#-build-from-source)
- 🛠️ [Launch service from source](#-launch-service-from-source)
- 📚 [Documentation](#-documentation)
- 📜 [Roadmap](#-roadmap)
- 🏄 [Community](#-community)
- 🙌 [Contributing](#-contributing)

</details>

## 💡 What is RAGFlow?

[RAGFlow](https://ragflow.io/) is an open-source RAG (Retrieval-Augmented Generation) engine based on deep document understanding. It offers a streamlined RAG workflow for businesses of any scale, combining LLM (Large Language Models) to provide truthful question-answering capabilities, backed by well-founded citations from various complex formatted data.

## 🎮 Demo

Try our demo at [https://demo.ragflow.io](https://demo.ragflow.io).

## 📌 Latest Updates

- 2024-05-30 Integrates [BCE](https://github.com/netease-youdao/BCEmbedding), [BGE](https://github.com/FlagOpen/FlagEmbedding), and [Colbert](https://github.com/stanford-futuredata/ColBERT) reranker models.
- 2024-05-28 Supports LLM Baichuan and VolcanoArk.
- 2024-05-23 Supports [RAPTOR](https://arxiv.org/html/2401.18059v1) for better text retrieval.
- 2024-05-21 Supports streaming output and text chunk retrieval API. 
- 2024-05-15 Integrates OpenAI GPT-4o.
- 2024-05-08 Integrates LLM DeepSeek-V2.
- 2024-04-26 Adds file management.
- 2024-04-19 Supports conversation API ([detail](./docs/references/api.md)).
- 2024-04-16 Integrates an embedding model 'bce-embedding-base_v1' from [BCEmbedding](https://github.com/netease-youdao/BCEmbedding), and [FastEmbed](https://github.com/qdrant/fastembed), which is designed specifically for light and speedy embedding.
- 2024-04-11 Supports [Xinference](./docs/guides/deploy_local_llm.md) for local LLM deployment.
- 2024-04-10 Adds a new layout recognition model for analyzing legal documents.
- 2024-04-08 Supports [Ollama](./docs/guides/deploy_local_llm.md) for local LLM deployment.
- 2024-04-07 Supports Chinese UI.

## 🌟 Key Features

### 🍭 **"Quality in, quality out"**

- [Deep document understanding](./deepdoc/README.md)-based knowledge extraction from unstructured data with complicated formats.
- Finds "needle in a data haystack" of literally unlimited tokens.

### 🍱 **Template-based chunking**

- Intelligent and explainable.
- Plenty of template options to choose from.

### 🌱 **Grounded citations with reduced hallucinations**

- Visualization of text chunking to allow human intervention.
- Quick view of the key references and traceable citations to support grounded answers.

### 🍔 **Compatibility with heterogeneous data sources**

- Supports Word, slides, excel, txt, images, scanned copies, structured data, web pages, and more.

### 🛀 **Automated and effortless RAG workflow**

- Streamlined RAG orchestration catered to both personal and large businesses.
- Configurable LLMs as well as embedding models.
- Multiple recall paired with fused re-ranking.
- Intuitive APIs for seamless integration with business.

## 🔎 System Architecture

<div align="center" style="margin-top:20px;margin-bottom:20px;">
<img src="https://github.com/infiniflow/ragflow/assets/12318111/d6ac5664-c237-4200-a7c2-a4a00691b485" width="1000"/>
</div>

## 🎬 Get Started

### 📝 Prerequisites

- CPU >= 4 cores
- RAM >= 16 GB
- Disk >= 50 GB
- Docker >= 24.0.0 & Docker Compose >= v2.26.1
  > If you have not installed Docker on your local machine (Windows, Mac, or Linux), see [Install Docker Engine](https://docs.docker.com/engine/install/).

### 🚀 Start up the server

1. Ensure `vm.max_map_count` >= 262144 ([more](./docs/guides/max_map_count.md)):

   > To check the value of `vm.max_map_count`:
   >
   > ```bash
   > $ sysctl vm.max_map_count
   > ```
   >
   > Reset `vm.max_map_count` to a value at least 262144 if it is not.
   >
   > ```bash
   > # In this case, we set it to 262144:
   > $ sudo sysctl -w vm.max_map_count=262144
   > ```
   >
   > This change will be reset after a system reboot. To ensure your change remains permanent, add or update the `vm.max_map_count` value in **/etc/sysctl.conf** accordingly:
   >
   > ```bash
   > vm.max_map_count=262144
   > ```

2. Clone the repo:

   ```bash
   $ git clone https://github.com/infiniflow/ragflow.git
   ```

3. Build the pre-built Docker images and start up the server:

   > Running the following commands automatically downloads the *dev* version RAGFlow Docker image. To download and run a specified Docker version, update `RAGFLOW_VERSION` in **docker/.env** to the intended version, for example `RAGFLOW_VERSION=v0.7.0`, before running the following commands.

   ```bash
   $ cd ragflow/docker
   $ chmod +x ./entrypoint.sh
   $ docker compose up -d
   ```
   

   > The core image is about 9 GB in size and may take a while to load.

4. Check the server status after having the server up and running:

   ```bash
   $ docker logs -f ragflow-server
   ```

   _The following output confirms a successful launch of the system:_

   ```bash
       ____                 ______ __
      / __ \ ____ _ ____ _ / ____// /____  _      __
     / /_/ // __ `// __ `// /_   / // __ \| | /| / /
    / _, _// /_/ // /_/ // __/  / // /_/ /| |/ |/ /
   /_/ |_| \__,_/ \__, //_/    /_/ \____/ |__/|__/
                 /____/

    * Running on all addresses (0.0.0.0)
    * Running on http://127.0.0.1:9380
    * Running on http://x.x.x.x:9380
    INFO:werkzeug:Press CTRL+C to quit
   ```
   > If you skip this confirmation step and directly log in to RAGFlow, your browser may prompt a `network anomaly` error because, at that moment, your RAGFlow may not be fully initialized.  

5. In your web browser, enter the IP address of your server and log in to RAGFlow.
   > With default settings, you only need to enter `http://IP_OF_YOUR_MACHINE` (**sans** port number) as the default HTTP serving port `80` can be omitted when using the default configurations.
6. In [service_conf.yaml](./docker/service_conf.yaml), select the desired LLM factory in `user_default_llm` and update the `API_KEY` field with the corresponding API key.

   > See [./docs/guides/llm_api_key_setup.md](./docs/guides/llm_api_key_setup.md) for more information.

   _The show is now on!_

## 🔧 Configurations

When it comes to system configurations, you will need to manage the following files:

- [.env](./docker/.env): Keeps the fundamental setups for the system, such as `SVR_HTTP_PORT`, `MYSQL_PASSWORD`, and `MINIO_PASSWORD`.
- [service_conf.yaml](./docker/service_conf.yaml): Configures the back-end services.
- [docker-compose.yml](./docker/docker-compose.yml): The system relies on [docker-compose.yml](./docker/docker-compose.yml) to start up.

You must ensure that changes to the [.env](./docker/.env) file are in line with what are in the [service_conf.yaml](./docker/service_conf.yaml) file.

> The [./docker/README](./docker/README.md) file provides a detailed description of the environment settings and service configurations, and you are REQUIRED to ensure that all environment settings listed in the [./docker/README](./docker/README.md) file are aligned with the corresponding configurations in the [service_conf.yaml](./docker/service_conf.yaml) file.

To update the default HTTP serving port (80), go to [docker-compose.yml](./docker/docker-compose.yml) and change `80:80` to `<YOUR_SERVING_PORT>:80`.

> Updates to all system configurations require a system reboot to take effect:
>
> ```bash
> $ docker-compose up -d
> ```

## 🛠️ Build from source

To build the Docker images from source:

```bash
$ git clone https://github.com/infiniflow/ragflow.git
$ cd ragflow/
$ docker build -t infiniflow/ragflow:dev .
$ cd ragflow/docker
$ chmod +x ./entrypoint.sh
$ docker compose up -d
```

## 🛠️ Launch service from source

To launch the service from source:

1. Clone the repository: 

   ```bash
   $ git clone https://github.com/infiniflow/ragflow.git
   $ cd ragflow/
   ```

2. Create a virtual environment, ensuring that Anaconda or Miniconda is installed:

   ```bash
   $ conda create -n ragflow python=3.11.0
   $ conda activate ragflow
   $ pip install -r requirements.txt
   ```
   
   ```bash
   # If your CUDA version is higher than 12.0, run the following additional commands:
   $ pip uninstall -y onnxruntime-gpu
   $ pip install onnxruntime-gpu --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/
   ```

3. Copy the entry script and configure environment variables:

   ```bash
   # Get the Python path:
   $ which python
   # Get the ragflow project path:
   $ pwd
   ```
   
   ```bash
   $ cp docker/entrypoint.sh .
   $ vi entrypoint.sh
   ```

   ```bash
   # Adjust configurations according to your actual situation (the following two export commands are newly added):
   # - Assign the result of `which python` to `PY`.
   # - Assign the result of `pwd` to `PYTHONPATH`.
   # - Comment out `LD_LIBRARY_PATH`, if it is configured.
   # - Optional: Add Hugging Face mirror.
   PY=${PY}
   export PYTHONPATH=${PYTHONPATH}
   export HF_ENDPOINT=https://hf-mirror.com
   ```

4. Launch the third-party services (MinIO, Elasticsearch, Redis, and MySQL):

   ```bash
   $ cd docker
   $ docker compose -f docker-compose-base.yml up -d 
   ```

5. Check the configuration files, ensuring that:

   - The settings in **docker/.env** match those in **conf/service_conf.yaml**. 
   - The IP addresses and ports for related services in **service_conf.yaml** match the local machine IP and ports exposed by the container.

6. Launch the RAGFlow backend service:

   ```bash
   $ chmod +x ./entrypoint.sh
   $ bash ./entrypoint.sh
   ```

7. Launch the frontend service:

   ```bash
   $ cd web
   $ npm install --registry=https://registry.npmmirror.com --force
   $ vim .umirc.ts
   # Update proxy.target to 127.0.0.1:9380
   $ npm run dev 
   ```

8. Deploy the frontend service:

   ```bash
   $ cd web
   $ npm install --registry=https://registry.npmmirror.com --force
   $ umi build
   $ mkdir -p /ragflow/web
   $ cp -r dist /ragflow/web
   $ apt install nginx -y
   $ cp ../docker/nginx/proxy.conf /etc/nginx
   $ cp ../docker/nginx/nginx.conf /etc/nginx
   $ cp ../docker/nginx/ragflow.conf /etc/nginx/conf.d
   $ systemctl start nginx
   ```

## 📚 Documentation

- [Quickstart](./docs/quickstart.md)
- [FAQ](./docs/references/faq.md)

## 📜 Roadmap

See the [RAGFlow Roadmap 2024](https://github.com/infiniflow/ragflow/issues/162)

## 🏄 Community

- [Discord](https://discord.gg/4XxujFgUN7)
- [Twitter](https://twitter.com/infiniflowai)

## 🙌 Contributing

RAGFlow flourishes via open-source collaboration. In this spirit, we embrace diverse contributions from the community. If you would like to be a part, review our [Contribution Guidelines](./docs/references/CONTRIBUTING.md) first.
