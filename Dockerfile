# OCI package for the Linux CLI distribution of MForce.
# The original Termux launch script is intentionally invoked with bash,
# bypassing its Termux-specific shebang inside the Linux container.
FROM debian:bookworm-slim

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       bash ca-certificates coreutils curl git iproute2 jq ncurses-bin \
       netcat-openbsd python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/mforce
COPY . /opt/mforce/
RUN chmod +x /opt/mforce/xrm742.sh \
    && mkdir -p /opt/mforce/.cache \
    && useradd --system --create-home --shell /bin/bash mforce \
    && chown -R mforce:mforce /opt/mforce
USER mforce

ENV TERM=xterm-256color
ENTRYPOINT ["/bin/bash", "/opt/mforce/xrm742.sh"]
