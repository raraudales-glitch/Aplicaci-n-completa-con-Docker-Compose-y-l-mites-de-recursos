
FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends stress-ng procps && \
    rm -rf /var/lib/apt/lists/*

CMD ["stress-ng", "--cpu", "2", "--vm", "1", "--vm-bytes", "256M", "--timeout", "300s", "--metrics-brief"]
