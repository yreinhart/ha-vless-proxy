# VLESS SOCKS Proxy

This app creates a private, TCP-only SOCKS5 endpoint on Home Assistant's
internal app network. Requests sent to that proxy leave through the configured
VLESS server. Everything else keeps the normal Home Assistant network route.

## Setup

1. Obtain a complete VLESS share link beginning with `vless://` from your VPN
   or proxy provider.
2. Paste the link into **VLESS URI**.
3. Keep the log level at `warning`, save, and start the app.
4. Open the app log and copy the line beginning with `SOCKS5 URL:`. The hostname
   depends on how the app repository was installed, so always use the value
   printed by your own installation.

The VLESS link contains connection credentials. Do not publish it or include it
in screenshots and support requests.

## Telegram Bot example

In the Telegram Bot integration, select polling and paste the complete URL from
the app log into **Proxy URL**. It will look similar to:

```text
socks5://7ce2fdf4-vless-proxy:1080
```

The exact prefix may differ. Only the Telegram integration uses this proxy;
other Home Assistant traffic remains direct.

## Supported links

The parser supports TCP/RAW, WebSocket, gRPC, HTTPUpgrade, and XHTTP transports,
with REALITY, TLS, or no transport security. A tested configuration is VLESS +
XTLS Vision + REALITY over TCP.

The SOCKS5 listener supports TCP connections only. It has no username/password
because it is isolated on the private Home Assistant app network. Port 1080 is
not exposed to the host or LAN.

## Troubleshooting

- `Configuration error` at startup means the URI is incomplete, malformed, or
  uses an unsupported transport/security combination.
- If Xray starts but the client cannot connect, confirm that you copied the
  exact SOCKS5 URL from the current app log.
- If the SOCKS endpoint works but the destination does not, create a fresh
  VLESS link, try another server, and restart the app.
- Use `debug` logging only temporarily. Xray does not receive the original
  `vless://` URI as a log value, but debug logs can still expose destinations.

---

# Настройка на русском

Приложение создаёт внутренний TCP SOCKS5-прокси Home Assistant и отправляет его
трафик через VLESS. Остальной трафик Home Assistant продолжает идти напрямую.

1. Получите у своего VPN- или прокси-провайдера полную ссылку, начинающуюся с
   `vless://`.
2. Вставьте её в поле **Ссылка VLESS**, сохраните параметры и запустите
   приложение.
3. Откройте журнал и скопируйте строку `SOCKS5 URL:`. Адрес зависит от способа
   установки репозитория, поэтому используйте адрес именно из своего журнала.
4. В интеграции Telegram Bot выберите polling и вставьте этот адрес в поле
   **Proxy URL**.

Ссылка VLESS содержит секрет подключения. Не публикуйте её. Порт 1080 доступен
только во внутренней сети приложений Home Assistant и не открыт в домашнюю сеть.
