"""
OBC hardware registry consumer — Ecosystem Integration I1.

The canonical hardware catalog lives in Oh-Ben-Claw's Rust registry
(``src/peripherals/registry.rs``) and is exported by its ``emit-registry``
binary as ``registry.json`` (``{schema_version, boards[], accessories[]}``).
Accelerapp consumes that generated document — bundled alongside this module
and refreshed on each registry export — instead of re-typing board data.

Refresh flow::

    # in Oh-Ben-Claw
    cargo run --bin emit-registry -- registry/registry.json
    # copy to consumers
    cp registry/registry.json ../Accelerapp/src/accelerapp/hardware/registry.json

Use :func:`load_registry` for the bundled catalog (or pass a path /
set ``OBC_REGISTRY_PATH``), then :func:`platform_for_board` to route a
registry board onto an Accelerapp code-generation platform.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

#: The registry.json schema this consumer understands. Must match the
#: ``schema_version`` in the document (mirrors OBC's REGISTRY_SCHEMA_VERSION).
SUPPORTED_SCHEMA_VERSION = 1

#: Environment variable overriding the bundled registry document.
REGISTRY_PATH_ENV = "OBC_REGISTRY_PATH"

_BUNDLED = Path(__file__).parent / "registry.json"


class RegistrySchemaError(RuntimeError):
    """The registry document's schema_version is unsupported."""


@dataclass(frozen=True)
class Board:
    """One board record from the generated registry (mirror of Rust ``BoardInfo``)."""

    name: str
    vid: int
    pid: int
    architecture: str
    transport: str
    capabilities: List[str] = field(default_factory=list)
    vendor: str = ""
    ecosystem: str = ""
    connectors: List[str] = field(default_factory=list)

    def has_capability(self, cap: str) -> bool:
        return cap in self.capabilities


@dataclass(frozen=True)
class Accessory:
    """One accessory record (mirror of Rust ``AccessoryInfo``)."""

    name: str
    description: str
    bus: str
    capabilities: List[str] = field(default_factory=list)
    compatible_boards: List[str] = field(default_factory=list)
    default_i2c_addr: Optional[int] = None
    connector: Optional[str] = None


@dataclass(frozen=True)
class Registry:
    """The full parsed registry document."""

    schema_version: int
    boards: List[Board]
    accessories: List[Accessory]

    # ── Lookups ────────────────────────────────────────────────────────────

    def find_board(self, name: str) -> Optional[Board]:
        """First board with this registry name (names may repeat across USB ids)."""
        return next((b for b in self.boards if b.name == name), None)

    def find_by_usb(self, vid: int, pid: int) -> Optional[Board]:
        """Board matching a USB VID/PID pair, if any."""
        return next((b for b in self.boards if b.vid == vid and b.pid == pid), None)

    def boards_with_capability(self, cap: str) -> List[Board]:
        return [b for b in self.boards if b.has_capability(cap)]

    def find_accessory(self, name: str) -> Optional[Accessory]:
        return next((a for a in self.accessories if a.name == name), None)

    def board_names(self) -> List[str]:
        """Distinct board names, registry order preserved."""
        seen: Dict[str, None] = {}
        for b in self.boards:
            seen.setdefault(b.name, None)
        return list(seen)


def _parse_board(raw: Dict[str, Any]) -> Board:
    return Board(
        name=raw["name"],
        vid=int(raw["vid"]),
        pid=int(raw["pid"]),
        architecture=raw.get("architecture", ""),
        transport=raw.get("transport", ""),
        capabilities=list(raw.get("capabilities", [])),
        vendor=raw.get("vendor", ""),
        ecosystem=raw.get("ecosystem", ""),
        connectors=list(raw.get("connectors", [])),
    )


def _parse_accessory(raw: Dict[str, Any]) -> Accessory:
    return Accessory(
        name=raw["name"],
        description=raw.get("description", ""),
        bus=raw.get("bus", ""),
        capabilities=list(raw.get("capabilities", [])),
        compatible_boards=list(raw.get("compatible_boards", [])),
        default_i2c_addr=raw.get("default_i2c_addr"),
        connector=raw.get("connector"),
    )


def load_registry(path: Optional[os.PathLike] = None) -> Registry:
    """
    Load and validate a registry document.

    Resolution order: explicit ``path`` argument → ``OBC_REGISTRY_PATH`` env
    var → the bundled ``registry.json``.

    Raises:
        RegistrySchemaError: on an unsupported ``schema_version``.
        FileNotFoundError / json.JSONDecodeError: on a missing or invalid file.
    """
    resolved = Path(path) if path else Path(os.environ.get(REGISTRY_PATH_ENV, _BUNDLED))
    with open(resolved, encoding="utf-8") as f:
        doc = json.load(f)

    version = doc.get("schema_version")
    if version != SUPPORTED_SCHEMA_VERSION:
        raise RegistrySchemaError(
            f"registry.json schema_version {version!r} is not supported "
            f"(this consumer understands {SUPPORTED_SCHEMA_VERSION}); "
            "regenerate with Oh-Ben-Claw's emit-registry or update Accelerapp"
        )

    return Registry(
        schema_version=version,
        boards=[_parse_board(b) for b in doc.get("boards", [])],
        accessories=[_parse_accessory(a) for a in doc.get("accessories", [])],
    )


@lru_cache(maxsize=1)
def default_registry() -> Registry:
    """The bundled registry, parsed once per process."""
    return load_registry()


# ── Board → Accelerapp platform routing ──────────────────────────────────────

def platform_for_board(board: Board) -> Optional[str]:
    """
    Map a registry board onto an Accelerapp code-generation platform name
    (as accepted by :func:`accelerapp.platforms.get_platform`).

    Returns ``None`` for boards Accelerapp does not generate firmware for
    (Linux SBC hosts other than Raspberry Pi, USB bridges, etc.).
    """
    ident = f"{board.name} {board.architecture} {board.ecosystem}".lower()

    # Order matters: check the most specific families first.
    if "m5stack" in ident or board.name.startswith("m5"):
        return "m5stack"
    if "esp32" in ident or "esp8266" in ident:
        return "esp32"
    if "rp2040" in ident or "rp2350" in ident or "pico" in ident:
        return "raspberry_pi_pico"
    if "stm32h7" in ident:
        return "stm32h7"
    if "stm32f4" in ident or "f401" in ident or "f411" in ident:
        return "stm32f4"
    if "stm32" in ident or "nucleo" in ident:
        return "stm32"
    if "nrf53" in ident:
        return "nrf53"
    if "nrf52" in ident or "nrf" in ident or "nordic" in ident:
        return "nrf52"
    if "atmega" in ident or "avr" in ident or "arduino" in ident:
        return "arduino"
    # Raspberry Pi SBCs run host-side Python (not Pico-class MCUs, caught above).
    if "raspberry-pi" in board.name or "broadcom" in ident:
        return "raspberry_pi"
    return None


def boards_for_platform(platform_name: str, registry: Optional[Registry] = None) -> List[Board]:
    """All registry boards that route to the given Accelerapp platform."""
    reg = registry or default_registry()
    return [b for b in reg.boards if platform_for_board(b) == platform_name.lower()]
