"""
Tests for the shared OBC firmware template consumer (Ecosystem Integration I6).
"""

import json

import pytest

from accelerapp.firmware.obc_templates import (
    NODE_ID_PLACEHOLDER,
    SUPPORTED_TEMPLATES_SCHEMA_VERSION,
    TemplatesSchemaError,
    codegen_route,
    load_templates,
    template_for_board,
)
from accelerapp.hardware.registry import load_registry


class TestLoadTemplates:
    def test_bundled_templates_load(self):
        templates = load_templates()
        assert len(templates) > 20
        boards = [t.board for t in templates]
        assert "esp32-s3" in boards
        assert len(boards) == len(set(boards)), "one template per board"

    def test_unsupported_schema_raises(self, tmp_path):
        p = tmp_path / "templates.json"
        p.write_text(json.dumps({"schema_version": 999, "templates": []}), encoding="utf-8")
        with pytest.raises(TemplatesSchemaError):
            load_templates(p)

    def test_every_template_is_a_valid_obc_node_sketch(self):
        for t in load_templates():
            assert t.filename.endswith(".ino")
            assert "void announce()" in t.source
            assert "void loop()" in t.source
            assert NODE_ID_PLACEHOLDER in t.source


class TestTemplateForBoard:
    def test_node_id_substitution(self):
        t = template_for_board("esp32-s3", node_id="vision-agent")
        assert t is not None
        assert 'OBC_NODE_ID = "vision-agent"' in t.source
        assert NODE_ID_PLACEHOLDER not in t.source

    def test_unknown_board_is_none(self):
        assert template_for_board("not-a-board") is None

    def test_native_hosts_have_no_template(self):
        # SBC hosts run the full agent, not flashed firmware.
        assert template_for_board("nanopi-neo3") is None


class TestCodegenRoute:
    def test_flashable_esp32_gets_platform_and_template(self):
        reg = load_registry()
        board = reg.find_board("esp32-s3")
        platform, template = codegen_route(board)
        assert platform == "esp32"
        assert template is not None
        assert template.board == "esp32-s3"

    def test_host_board_routes_to_platform_only(self):
        reg = load_registry()
        board = reg.find_board("nanopi-neo3")
        assert board is not None
        platform, template = codegen_route(board)
        assert template is None  # native transport → no flashable scaffold
        # platform may be None (generic SBC) — either way no crash.

    def test_templates_align_with_registry_flashables(self):
        """Every serial/probe registry board has a shared template (drift guard)."""
        reg = load_registry()
        template_boards = {t.board for t in load_templates()}
        flashable = {b.name for b in reg.boards if b.transport in ("serial", "probe")}
        assert template_boards == flashable
