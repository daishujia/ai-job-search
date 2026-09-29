# Minimal aria2 daemon for nas-mcp. Runs as the NAS 'agent' user (see docker-compose.yml).
FROM debian:12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends aria2 ca-certificates \
 && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["aria2c", "--conf-path=/config/aria2.conf"]
