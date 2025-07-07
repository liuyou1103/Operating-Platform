#!/bin/bash

# 配置参数（可修改）
CONTAINER_NAME="unruffled_kapitsa"      # 容器名称
IMAGE_NAME="baai-flask-server-release"          # 镜像名称（默认使用 nginx）
PORTS="-p 8080:8080"                 # 端口映射（主机端口:容器端口）
VOLUMES="-v /home/agilex/Documents/Ryu-Yang/Operating-Platform/:/home/agilex/Documents/Ryu-Yang/Operating-Platform/"  # 卷挂载（可选）
VOLUMES2="-v /home/agilex/Documents/liuyou1103/release/Operating-Platform/operating_platform/server/:/app/code/"  # 卷挂载（可选）
POLICY = "--privileged=true"
RESTART_POLICY="--restart unless-stopped"  # 重启策略

# 检查容器是否存在
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    # 容器存在，检查是否正在运行
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "容器 '${CONTAINER_NAME}' 已经在运行，无需操作。"
    else
        # 容器存在但未运行，启动它
        echo "启动已存在的容器 '${CONTAINER_NAME}'..."
        docker start ${CONTAINER_NAME}
    fi
else
    # 容器不存在，创建并运行
    echo "创建并启动新容器 '${CONTAINER_NAME}'..."
    docker run -d --name ${CONTAINER_NAME} ${PORTS} ${VOLUMES} ${VOLUMES2} ${POLICY} ${RESTART_POLICY} ${IMAGE_NAME}
fi

# 可选：检查容器状态
echo "当前容器状态："
docker ps -a --filter "name=${CONTAINER_NAME}" --format 'table {{.Names}}\t{{.Status}}'
