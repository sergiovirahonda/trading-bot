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