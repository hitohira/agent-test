# ベースイメージ（軽量なPython環境）
FROM python:3.11-slim

# 作業ディレクトリを作成
WORKDIR /app

# Pythonパッケージのインストール 
COPY requirements.txt .
RUN pip install -r requirements.txt

# スクリプト資材をコンテナにコピー
COPY ./app/ .

# mcp_test.py を直接実行
CMD ["python", "mcp_test.py"]
# CMD ["bash"]

