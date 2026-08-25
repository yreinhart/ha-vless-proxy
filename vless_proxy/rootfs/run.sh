#!/usr/bin/with-contenv bashio
set -euo pipefail

readonly XRAY_CONFIG="/tmp/xray.json"
umask 077

bashio::log.info "Generating Xray configuration"

if ! python3 /usr/local/bin/generate_xray_config.py \
    /data/options.json \
    "${XRAY_CONFIG}"; then
    bashio::log.fatal "Invalid VLESS configuration. Check the app options."
    exit 1
fi

app_slug=""
if app_slug="$(bashio::api.supervisor 'GET' '/addons/self/info' '' '.slug')"; then
    app_host="${app_slug//_/-}"
    bashio::log.info "SOCKS5 URL: socks5://${app_host}:1080"
else
    bashio::log.warning "Could not determine the internal app hostname."
    bashio::log.warning "Use the slug shown by Supervisor, replace underscores with hyphens, and append :1080."
fi

bashio::log.info "Starting Xray"
exec /usr/local/bin/xray run -config "${XRAY_CONFIG}"

