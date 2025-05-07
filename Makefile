.SILENT:

build:
	echo "Attempting to build trading bot image..." && \
	( \
		export DOCKER_DEFAULT_PLATFORM=linux/arm64 && docker build -t trading-bot . \
	) || ( \
		echo "Failed to build trading bot image" && \
		exit 1 \
	) && \
	echo "Successfully built trading bot image..."

deploy:
	echo "Attempting to deploy trading bot image..." && \
	( \
		kubectl apply -f resources/local/redis.yaml && \
		kubectl apply -f resources/local/configmap.yaml && \
		kubectl apply -f resources/local/bot.yaml \
	)|| ( \
		echo "Failed to deploy trading bot image" && \
		exit 1 \
	) && \
	echo "Successfully deployed trading bot image..."