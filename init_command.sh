#!/bin/sh
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
sudo apt update -y
sudo apt upgrade -y
sudo apt install python3-pip -y
sudo apt install python3-venv -y
sudo apt install python3-dev default-libmysqlclient-dev build-essential -y
pip install wheel
pip install flask flask-migrate flask_restful python-dotenv mysqlclient requests bs4 pandas konlpy sklearn sentence_transformers
