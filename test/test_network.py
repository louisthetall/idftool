"""Network ports (``rfc2217://``): no device required."""
import serial

from idftool import network
from idftool.commands.misc import _option_value


def test_local_ports_are_left_alone(monkeypatch):
    import esptool.loader

    monkeypatch.setattr(serial, "protocol_handler_packages", ["serial.urlhandler"])
    monkeypatch.setattr(esptool.loader, "SYNC_TIMEOUT", 0.1)
    network.prepare("/dev/ttyUSB0")
    network.prepare(None)
    assert serial.protocol_handler_packages == ["serial.urlhandler"]
    assert esptool.loader.SYNC_TIMEOUT == 0.1


def test_a_network_port_gets_the_long_sync_and_our_handler(monkeypatch):
    import esptool.loader

    monkeypatch.setattr(serial, "protocol_handler_packages", ["serial.urlhandler"])
    monkeypatch.setattr(esptool.loader, "SYNC_TIMEOUT", 0.1)
    network.prepare("rfc2217://127.0.0.1:4000")
    network.prepare("rfc2217://127.0.0.1:4001")
    assert serial.protocol_handler_packages == [network.URL_HANDLERS, "serial.urlhandler"]
    assert esptool.loader.SYNC_TIMEOUT == network.NETWORK_SYNC_TIMEOUT
    port = serial.serial_for_url("rfc2217://127.0.0.1:4000", do_not_open=True)
    assert isinstance(port, network.Rfc2217Serial)


def test_settings_are_renegotiated_only_when_they_change(monkeypatch):
    negotiations = []
    monkeypatch.setattr(serial.rfc2217.Serial, "_reconfigure_port",
                        lambda port: negotiations.append(port.baudrate))
    port = network.Rfc2217Serial()
    port.is_open = True
    port._reconfigure_port()
    port.timeout = 3
    port.timeout = 0.1
    assert negotiations == [9600]
    port.baudrate = 460800
    port.timeout = 3
    assert negotiations == [9600, 460800]


def test_the_port_is_found_in_any_spelling():
    assert _option_value(["--port", "rfc2217://a:1", "chip-id"], "-p", "--port") == "rfc2217://a:1"
    assert _option_value(["--port=rfc2217://a:1"], "-p", "--port") == "rfc2217://a:1"
    assert _option_value(["-prfc2217://a:1"], "-p", "--port") == "rfc2217://a:1"
    assert _option_value(["chip-id"], "-p", "--port") is None
