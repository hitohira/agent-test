# イメージ名（必要に応じて変更可能）
IMAGE_NAME=weather-runner

# ビルドターゲット
build:
	docker build -t $(IMAGE_NAME) .

# 実行ターゲット（対話あり）
run:
	docker run -it --rm $(IMAGE_NAME)
