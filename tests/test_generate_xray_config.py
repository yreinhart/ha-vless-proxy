import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import unittest


SCRIPT = (
    Path(__file__).parents[1]
    / "vless_proxy"
    / "rootfs"
    / "usr"
    / "local"
    / "bin"
    / "generate_xray_config.py"
)
SPEC = importlib.util.spec_from_file_location("generate_xray_config", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class BuildXrayConfigTest(unittest.TestCase):
    def test_reality_tcp_redshield_style_uri(self):
        uri = (
            "vless://11111111-2222-3333-4444-555555555555@vpn.example:443"
            "?encryption=none&flow=xtls-rprx-vision&security=reality"
            "&sni=www.example.com&fp=chrome&pbk=PUBLIC_KEY&sid=a1b2c3"
            "&spx=%2F&type=tcp&headerType=none#RedShield"
        )
        config = MODULE.build_xray_config(
            {"vless_uri": uri, "log_level": "warning"}
        )

        inbound = config["inbounds"][0]
        outbound = config["outbounds"][0]
        user = outbound["settings"]["vnext"][0]["users"][0]
        reality = outbound["streamSettings"]["realitySettings"]

        self.assertEqual(inbound["listen"], "0.0.0.0")
        self.assertEqual(inbound["port"], 1080)
        self.assertFalse(inbound["settings"]["udp"])
        self.assertEqual(outbound["streamSettings"]["network"], "tcp")
        self.assertEqual(user["flow"], "xtls-rprx-vision")
        self.assertEqual(reality["publicKey"], "PUBLIC_KEY")
        self.assertEqual(reality["shortId"], "a1b2c3")
        self.assertEqual(reality["spiderX"], "/")

    def test_tls_websocket_uri(self):
        uri = (
            "vless://client-id@vpn.example:8443?security=tls&type=ws"
            "&sni=edge.example&host=edge.example&path=%2Ftelegram"
            "&alpn=h2%2Chttp%2F1.1&packetEncoding=xudp"
        )
        config = MODULE.build_xray_config({"vless_uri": uri})
        outbound = config["outbounds"][0]
        stream = outbound["streamSettings"]
        user = outbound["settings"]["vnext"][0]["users"][0]

        self.assertEqual(stream["network"], "ws")
        self.assertEqual(stream["wsSettings"]["path"], "/telegram")
        self.assertEqual(stream["tlsSettings"]["alpn"], ["h2", "http/1.1"])
        self.assertEqual(user["packetEncoding"], "xudp")

    def test_rejects_non_vless_uri(self):
        with self.assertRaises(MODULE.ConfigurationError):
            MODULE.build_xray_config({"vless_uri": "https://example.com"})

    def test_rejects_reality_without_public_key(self):
        uri = "vless://client-id@vpn.example:443?security=reality&type=tcp"
        with self.assertRaises(MODULE.ConfigurationError):
            MODULE.build_xray_config({"vless_uri": uri})

    def test_rejects_password_component(self):
        uri = "vless://client-id:password@vpn.example:443?security=tls&type=tcp"
        with self.assertRaises(MODULE.ConfigurationError):
            MODULE.build_xray_config({"vless_uri": uri})

    def test_main_writes_private_config_file(self):
        options = {
            "vless_uri": "vless://client-id@vpn.example:443?security=tls&type=tcp"
        }
        with tempfile.TemporaryDirectory() as directory:
            options_path = Path(directory) / "options.json"
            output_path = Path(directory) / "xray.json"
            options_path.write_text(json.dumps(options), encoding="utf-8")

            original_argv = MODULE.sys.argv
            MODULE.sys.argv = [str(SCRIPT), str(options_path), str(output_path)]
            try:
                self.assertEqual(MODULE.main(), 0)
            finally:
                MODULE.sys.argv = original_argv

            self.assertEqual(
                stat.S_IMODE(output_path.stat().st_mode),
                0o600,
            )


if __name__ == "__main__":
    unittest.main()

