# イメージ名（必要に応じて変更可能）
IMAGE_NAME=agent-any-command-runner

# ビルドターゲット
build:
	docker build -t $(IMAGE_NAME) .

# 実行ターゲット（対話あり）
run:
	docker run -it --rm $(IMAGE_NAME)

# 実行ターゲット（対話あり）
# Docker上の作成先をローカルのmount/にする
local:
	docker run -it -v $(CURDIR)/mount:/tmp --rm $(IMAGE_NAME)
