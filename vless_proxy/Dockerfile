ARG BUILD_FROM=ghcr.io/home-assistant/base:3.23

FROM ghcr.io/xtls/xray-core:26.3.27@sha256:592ec4d11f656db95598d01e76dbcc6e002d67360b96a5436500a938230f52c7 AS xray

FROM ${BUILD_FROM}

ARG BUILD_ARCH=unknown
ARG BUILD_VERSION=dev

RUN apk add --no-cache python3

COPY --from=xray /usr/local/bin/xray /usr/local/bin/xray
COPY rootfs /
COPY licenses /usr/share/licenses/ha-vless-proxy

RUN chmod 0755 /run.sh /usr/local/bin/generate_xray_config.py

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python3 -c "import socket; socket.create_connection(('127.0.0.1', 1080), 2).close()"

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.title="Home Assistant App: VLESS SOCKS Proxy" \
    org.opencontainers.image.description="Internal SOCKS5 proxy through a VLESS outbound" \
    org.opencontainers.image.source="https://github.com/yreinhart/ha-vless-proxy" \
    org.opencontainers.image.licenses="Apache-2.0 AND MPL-2.0"

CMD ["/run.sh"]

