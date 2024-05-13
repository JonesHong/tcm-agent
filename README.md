
先跑 ASR 


docker run -it --gpus all -p 9090:9090 ghcr.io/collabora/whisperlive-gpu:latest


# conda 
<!-- conda env remove -n tcm-agent -->
conda update --all -y
conda create -n  tcm-agent  python=3.8 -y
conda activate tcm-agent
conda install -c conda-forge jupyter -y
pip install -r requirements.txt


<!-- 在windows -->


##  install pyopenjtalk
## 參考 https://blog.csdn.net/qq_44712946/article/details/131820011

<!-- 加入環境變數 -->
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.36.32532\bin\Hostx64\x64

pip install pyopenjtalk  -i https://pypi.tuna.tsinghua.edu.cn/simple --no-build-isolation



## run redis.service.py
conda activate tcm-agent && python redis.service.py --port 51201



## Redis
docker run -d -p 51201:6379  --name 51201-redis -d --restart=always redis


