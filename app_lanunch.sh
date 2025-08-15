#!/bin/bash
# 加载conda环境变量（关键步骤）
source /home/ubuntu/anaconda3/etc/profile.d/conda.sh
LOG_DIR="/data/workspace/news_translation_service/logs"

TIMESTAMP=$(date +%Y%m%d)
# 激活conda环境
conda activate /data/workspace/envs/newsenv

# 启动Flask应用
nohup python /data/workspace/news_translation_service/app.py >/dev/null 2>>$LOG_DIR/app_$TIMESTAMP.log &