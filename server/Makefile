build:
	docker build -t wolf-logic-api-server .

run_local:
	docker run -p 8000:8000 -v $(shell pwd):/app wolf-logic-api-server --env-file .env

.PHONY: build run_local
