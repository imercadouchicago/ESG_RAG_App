IMAGE_NAME=langchain-rag-app
LOCAL_HOST_DIR = $(shell pwd)
CONTAINER_SRC_DIR = /app/src
DATA_DIR_PATH = $(CONTAINER_SRC_DIR)/data

.PHONY: build interactive pull-models \
		streamlit streamlit-gpu down

# build:
# 	docker build -t $(IMAGE_NAME) .

# interactive: build
# 	docker run -it \
# 	-v "$(LOCAL_HOST_DIR):$(CONTAINER_SRC_DIR)" \
# 	$(IMAGE_NAME) /bin/bash

# streamlit: build
# 	docker run \
# 	-v "$(LOCAL_HOST_DIR):$(CONTAINER_SRC_DIR)" \
#	-e $(DATA_DIR_PATH) \
# 	-p 8501:8501 -p 11434:11434 $(IMAGE_NAME)

pull-models:
	docker compose up -d ollama
	sleep 5  # Wait for Ollama service to fully start
	curl -X POST http://localhost:11434/api/pull -d '{"name": "nomic-embed-text:latest"}'
	curl -X POST http://localhost:11434/api/pull -d '{"name": "llama3:instruct"}'