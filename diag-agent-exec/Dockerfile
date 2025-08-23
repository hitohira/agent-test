# ベースイメージ（軽量なPython環境）
FROM python:3.11-slim

# 一般ユーザ作成
RUN useradd -m pyuser

# 作業ディレクトリを作成
WORKDIR /app

# Pythonパッケージのインストール 
COPY requirements.txt .
RUN pip install -r requirements.txt

# スクリプト資材をコンテナにコピー
COPY ./app/ .

# 一般ユーザに切り替え
USER pyuser

# weather.py を直接実行
CMD ["python", "ai_agent.py"]
# CMD ["bash"]

