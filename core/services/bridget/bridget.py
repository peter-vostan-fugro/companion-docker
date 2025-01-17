import logging
from typing import Dict, List

from bridges.bridges import Bridge
from bridges.serialhelper import Baudrate
from pydantic import BaseModel, conint
from serial.tools.list_ports_linux import SysFS, comports


class BridgeSpec(BaseModel):
    """Basic interface for 'bridges' links."""

    serial_path: str
    baud: Baudrate
    ip: str
    udp_port: conint(gt=1023, lt=65536)  # type: ignore

    def __str__(self) -> str:
        return f"{self.serial_path}:{self.baud}//{self.ip}:{self.udp_port}"

    def __hash__(self) -> int:
        return hash(str(self))


class Bridget:
    """Manager for 'bridges' links."""

    def __init__(self) -> None:
        self._bridges: Dict[BridgeSpec, Bridge] = {}

    def is_port_available(self, port: str) -> bool:
        if port in [bridge.serial_path for bridge in self._bridges]:
            return False
        try:
            with open(port, mode="r", encoding="utf-8"):
                pass
            return True
        except Exception:
            return False

    def available_serial_ports(self) -> List[str]:
        available_ports = []
        for port in comports():
            if not self.is_port_available(port.device):
                logging.debug(f"Port {port.device} found but not available.")
                continue
            available_ports.append(port.device)
            logging.debug(f"Port {port.device} found and available.")
        return available_ports

    def get_bridges(self) -> List[BridgeSpec]:
        return [spec for spec, bridge in self._bridges.items()]

    def add_bridge(self, bridge_spec: BridgeSpec) -> None:
        if bridge_spec in self._bridges:
            raise RuntimeError("Bridge already exist.")
        new_bridge = Bridge(SysFS(bridge_spec.serial_path), bridge_spec.baud, bridge_spec.ip, bridge_spec.udp_port)
        self._bridges[bridge_spec] = new_bridge

    def remove_bridge(self, bridge_spec: BridgeSpec) -> None:
        bridge = self._bridges.pop(bridge_spec, None)
        if bridge is None:
            raise RuntimeError("Bridge doesn't exist.")
        bridge.stop()

    def stop(self) -> None:
        logging.debug("Stopping Bridget and removing all bridges.")
        for bridge_spec in self._bridges:
            self.remove_bridge(bridge_spec)

    def __del__(self) -> None:
        self.stop()
