#!/usr/bin/env python3
"""Convert a VLESS share URI into a minimal Xray client configuration.

The URI is read from Home Assistant app options and is never written to logs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit


SOCKS_PORT = 1080


class ConfigurationError(ValueError):
    """Raised when the supplied app options cannot form a safe Xray config."""


def _first(query: dict[str, list[str]], *names: str, default: str = "") -> str:
    for name in names:
        values = query.get(name)
        if values:
            return values[0]
    return default


def _truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _require(value: str | None, field: str) -> str:
    if value is None or not str(value).strip():
        raise ConfigurationError(f"Required VLESS field is missing: {field}")
    return str(value).strip()


def _transport_settings(query: dict[str, list[str]]) -> tuple[str, dict[str, Any]]:
    transport = _first(query, "type", default="tcp").lower()
    aliases = {
        "raw": "tcp",
        "tcp": "tcp",
        "ws": "ws",
        "websocket": "ws",
        "grpc": "grpc",
        "httpupgrade": "httpupgrade",
        "xhttp": "xhttp",
        "splithttp": "xhttp",
    }
    if transport not in aliases:
        raise ConfigurationError(f"Unsupported VLESS transport type: {transport}")

    network = aliases[transport]
    settings: dict[str, Any] = {}

    if network == "tcp":
        header_type = _first(query, "headerType", default="none")
        if header_type != "none":
            settings["tcpSettings"] = {"header": {"type": header_type}}
    elif network == "ws":
        ws: dict[str, Any] = {"path": _first(query, "path", default="/")}
        host = _first(query, "host")
        if host:
            ws["headers"] = {"Host": host}
        settings["wsSettings"] = ws
    elif network == "grpc":
        grpc: dict[str, Any] = {
            "serviceName": _first(query, "serviceName", default="")
        }
        if _truthy(_first(query, "multiMode")):
            grpc["multiMode"] = True
        settings["grpcSettings"] = grpc
    elif network == "httpupgrade":
        upgrade: dict[str, Any] = {"path": _first(query, "path", default="/")}
        host = _first(query, "host")
        if host:
            upgrade["host"] = host
        settings["httpupgradeSettings"] = upgrade
    elif network == "xhttp":
        xhttp: dict[str, Any] = {"path": _first(query, "path", default="/")}
        for key in ("host", "mode"):
            value = _first(query, key)
            if value:
                xhttp[key] = value
        settings["xhttpSettings"] = xhttp

    return network, settings


def build_xray_config(options: dict[str, Any]) -> dict[str, Any]:
    """Build an Xray configuration from validated Home Assistant options."""
    uri = _require(options.get("vless_uri"), "vless_uri")
    parsed = urlsplit(uri)
    if parsed.scheme.lower() != "vless":
        raise ConfigurationError("The configuration must start with vless://")
    if parsed.password is not None:
        raise ConfigurationError("The VLESS URI must not contain a password component")

    client_id = _require(unquote(parsed.username or ""), "user ID")
    address = _require(parsed.hostname, "server address")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ConfigurationError("The VLESS server port is invalid") from exc
    if port is None:
        raise ConfigurationError("Required VLESS field is missing: server port")

    query = parse_qs(parsed.query, keep_blank_values=True)
    security = _first(query, "security", default="none").lower()
    if security not in {"none", "tls", "reality"}:
        raise ConfigurationError(f"Unsupported VLESS security type: {security}")

    network, transport = _transport_settings(query)
    stream: dict[str, Any] = {"network": network, "security": security, **transport}

    server_name = _first(query, "sni", "serverName", default=address)
    fingerprint = _first(query, "fp", "fingerprint", default="chrome")

    if security == "reality":
        public_key = _require(_first(query, "pbk", "publicKey"), "pbk/publicKey")
        reality: dict[str, Any] = {
            "serverName": server_name,
            "fingerprint": fingerprint,
            "publicKey": public_key,
            "shortId": _first(query, "sid", "shortId"),
        }
        spider_x = _first(query, "spx", "spiderX")
        if spider_x:
            reality["spiderX"] = spider_x
        stream["realitySettings"] = reality
    elif security == "tls":
        tls: dict[str, Any] = {
            "serverName": server_name,
            "fingerprint": fingerprint,
            "allowInsecure": _truthy(_first(query, "allowInsecure")),
        }
        alpn = [value for value in _first(query, "alpn").split(",") if value]
        if alpn:
            tls["alpn"] = alpn
        stream["tlsSettings"] = tls

    user: dict[str, Any] = {
        "id": client_id,
        "encryption": _first(query, "encryption", default="none"),
    }
    flow = _first(query, "flow")
    if flow:
        user["flow"] = flow
    packet_encoding = _first(query, "packetEncoding")
    if packet_encoding:
        user["packetEncoding"] = packet_encoding

    log_level = str(options.get("log_level", "warning")).lower()
    if log_level not in {"debug", "info", "warning", "error", "none"}:
        raise ConfigurationError("Unsupported log_level")

    return {
        "log": {"loglevel": log_level},
        "inbounds": [
            {
                "tag": "socks-in",
                "listen": "0.0.0.0",
                "port": SOCKS_PORT,
                "protocol": "socks",
                "settings": {"auth": "noauth", "udp": False},
            }
        ],
        "outbounds": [
            {
                "tag": "vless-out",
                "protocol": "vless",
                "settings": {
                    "vnext": [
                        {
                            "address": address,
                            "port": port,
                            "users": [user],
                        }
                    ]
                },
                "streamSettings": stream,
            }
        ],
        "routing": {
            "domainStrategy": "AsIs",
            "rules": [
                {
                    "type": "field",
                    "inboundTag": ["socks-in"],
                    "outboundTag": "vless-out",
                }
            ],
        },
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: generate_xray_config.py OPTIONS_JSON OUTPUT_JSON", file=sys.stderr)
        return 2

    try:
        options = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        config = build_xray_config(options)
        output = Path(sys.argv[2])
        output.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        output.chmod(0o600)
    except (OSError, json.JSONDecodeError, ConfigurationError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

