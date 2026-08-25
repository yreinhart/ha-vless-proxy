# Changelog

## 0.2.0-beta.1

- Publish a provider-independent Home Assistant App repository.
- Add `amd64` alongside `aarch64` using a multi-architecture GHCR image.
- Print the installation-specific internal SOCKS5 URL from Supervisor metadata.
- Store the generated Xray configuration on a memory-backed `/tmp` filesystem.
- Add a TCP watchdog, container health check, tests, and GitHub Actions builds.
- Keep Red Shield VPN VLESS + XTLS Vision + REALITY as a tested configuration.

## 0.1.1

- Disable the Supervisor Docker init wrapper so s6-overlay runs as PID 1.

## 0.1.0

- Initial private `aarch64` build for Red Shield VPN VLESS links.

