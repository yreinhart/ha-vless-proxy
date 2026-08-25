# VLESS SOCKS Proxy for Home Assistant

A Home Assistant App (formerly add-on) that turns a `vless://` share URI into
an internal, TCP-only SOCKS5 proxy powered by Xray-core.

The proxy is available only on Home Assistant's internal app network. It is not
published to your LAN. This lets one integration use VLESS while the rest of
Home Assistant keeps its normal route. Common VLESS configurations using
REALITY and XTLS Vision are supported.

## Installation

[![Open your Home Assistant instance and add this repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fyreinhart%2Fha-vless-proxy)

Or add this URL under **Settings → Apps → App store → Repositories**:

```text
https://github.com/yreinhart/ha-vless-proxy
```

Install **VLESS SOCKS Proxy**, paste the complete `vless://` URI, save, and
start the app. Its log prints the exact internal SOCKS5 URL to copy into a Home
Assistant integration.

For Telegram Bot, select polling and put that URL in **Proxy URL**. Only the
Telegram integration's requests will use VLESS.

## Supported configurations

- Architectures: `aarch64` and `amd64`
- Security: REALITY, TLS, or none
- Transports: TCP/RAW, WebSocket, gRPC, HTTPUpgrade, and XHTTP
- Tested configuration: VLESS + XTLS Vision + REALITY over TCP

See [app documentation](vless_proxy/DOCS.md) for setup and troubleshooting.

## Security

The VLESS URI is a secret. The app masks it in the Home Assistant UI, never
logs it, and writes the generated Xray configuration only to `/tmp`, which is a
memory-backed filesystem. Do not paste real connection URIs into issues.

The SOCKS5 endpoint deliberately has no authentication because it is limited to
Home Assistant's private app network. Do not modify the app to publish port
1080 to an untrusted network without adding authentication.

## Русский

Приложение преобразует ссылку `vless://` во внутренний SOCKS5-прокси Home
Assistant. Весь Home Assistant через VPN не направляется: прокси использует
только та интеграция, в которой вы явно укажете выведенный в журнале адрес.

Для Telegram Bot выберите polling и вставьте адрес из журнала приложения в
поле **Proxy URL**. Проверена конфигурация VLESS + XTLS Vision + REALITY через
TCP.

## Development

```bash
python3 -m unittest discover -s tests -v
bash -n vless_proxy/rootfs/run.sh
```

Container images for `aarch64` and `amd64` are built with the current Home
Assistant builder actions and published to GHCR after changes reach `main`.

## License

The app wrapper is licensed under Apache-2.0. Xray-core is distributed under
MPL-2.0; see [third-party notices](THIRD_PARTY_NOTICES.md).
