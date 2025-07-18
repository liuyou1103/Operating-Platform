#!/bin/bash

# 配置参数（可修改）
CONTAINER_NAME="baai_flask_server"      # 容器名称
IMAGE_NAME="baai-flask-server-release"  # 镜像名称
PORTS="-p 8080:8080"                    # 端口映射（主机端口:容器端口）
VOLUMES="-v /home/agilex/Documents/Operating-Platform/:/home/agilex/Documents/Ryu-Yang/Operating-Platform/"  # 卷挂载
VOLUMES2="-v /home/agilex/Documents/server/Operating-Platform/operating_platform/server/:/app/code/"  # 卷挂载
PRIVILEGED="--privileged=true"               # 特权模式（谨慎使用）
RESTART_POLICY="--restart unless-stopped"  # 重启策略

# 检查镜像是否存在，不存在则拉取
if ! docker images --format "{{.Repository}}" | grep -q "^${IMAGE_NAME}$"; then
    echo "镜像 '${IMAGE_NAME}' 不存在，正在拉取..."
    docker pull ${IMAGE_NAME}
fi

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
    docker run -d \
        --name ${CONTAINER_NAME} \
        ${PRIVILEGED} \
        ${RESTART_POLICY} \
        ${PORTS} \
        ${VOLUMES} \
        ${VOLUMES2} \
        ${IMAGE_NAME}
fi

# 检查容器状态
echo "当前容器状态："
docker ps -a --filter "name=${CONTAINER_NAME}" --format 'table {{.Names}}\t{{.Status}}'