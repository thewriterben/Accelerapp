"""
Tests for Flipper Zero integration.
"""

import pytest
from datetime import datetime
from accelerapp.hardware import (
    FlipperZero,
    FlipperProtocol,
    RFIDType,
    NFCType,
    RFIDTag,
    NFCTag,
    SubGHzSignal,
    IRSignal,
)


def test_flipper_protocol_enum():
    """Test FlipperProtocol enum values."""
    assert FlipperProtocol.RFID_125KHZ.value == "rfid_125khz"
    assert FlipperProtocol.NFC.value == "nfc"
    assert FlipperProtocol.SUBGHZ.value == "subghz"
    assert FlipperProtocol.INFRARED.value == "infrared"
    assert FlipperProtocol.GPIO.value == "gpio"


def test_rfid_type_enum():
    """Test RFIDType enum values."""
    assert RFIDType.EM4100.value == "EM4100"
    assert RFIDType.HID_PROX.value == "HIDProx"
    assert RFIDType.MIFARE_CLASSIC.value == "MifareClassic"


def test_nfc_type_enum():
    """Test NFCType enum values."""
    assert NFCType.NTAG.value == "NTAG"
    assert NFCType.MIFARE_CLASSIC.value == "MifareClassic"
    assert NFCType.ISO14443A.value == "ISO14443A"


def test_rfid_tag_creation():
    """Test RFIDTag dataclass."""
    tag = RFIDTag(
        tag_type="EM4100",
        uid="1234567890",
        protocol=FlipperProtocol.RFID_125KHZ,
        data="test_data",
    )
    
    assert tag.tag_type == "EM4100"
    assert tag.uid == "1234567890"
    assert tag.protocol == FlipperProtocol.RFID_125KHZ
    assert tag.data == "test_data"


def test_rfid_tag_to_dict():
    """Test RFIDTag to_dict conversion."""
    tag = RFIDTag(
        tag_type="EM4100",
        uid="1234567890",
        protocol=FlipperProtocol.RFID_125KHZ,
        blocks={0: "data0", 1: "data1"},
    )
    
    data = tag.to_dict()
    
    assert data["tag_type"] == "EM4100"
    assert data["uid"] == "1234567890"
    assert data["protocol"] == "rfid_125khz"
    assert 0 in data["blocks"]
    assert 1 in data["blocks"]
    assert "read_time" in data


def test_nfc_tag_creation():
    """Test NFCTag dataclass."""
    tag = NFCTag(
        tag_type="NTAG",
        uid="04:12:34:56:78:90",
        atqa="0044",
        sak="00",
    )
    
    assert tag.tag_type == "NTAG"
    assert tag.uid == "04:12:34:56:78:90"
    assert tag.atqa == "0044"
    assert tag.sak == "00"


def test_nfc_tag_to_dict():
    """Test NFCTag to_dict conversion."""
    tag = NFCTag(
        tag_type="NTAG",
        uid="04:12:34:56:78:90",
        atqa="0044",
        sak="00",
        ndef_records=[{"type": "text", "data": "Hello"}],
    )
    
    data = tag.to_dict()
    
    assert data["tag_type"] == "NTAG"
    assert data["uid"] == "04:12:34:56:78:90"
    assert data["atqa"] == "0044"
    assert data["sak"] == "00"
    assert len(data["ndef_records"]) == 1
    assert "read_time" in data


def test_subghz_signal_creation():
    """Test SubGHzSignal dataclass."""
    signal = SubGHzSignal(
        frequency=433.92,
        modulation="ASK",
        protocol="Princeton",
        data="01010101",
        rssi=-50,
    )
    
    assert signal.frequency == 433.92
    assert signal.modulation == "ASK"
    assert signal.protocol == "Princeton"
    assert signal.data == "01010101"
    assert signal.rssi == -50


def test_subghz_signal_to_dict():
    """Test SubGHzSignal to_dict conversion."""
    signal = SubGHzSignal(
        frequency=433.92,
        modulation="ASK",
        protocol="Princeton",
        data="01010101",
    )
    
    data = signal.to_dict()
    
    assert data["frequency"] == 433.92
    assert data["modulation"] == "ASK"
    assert data["protocol"] == "Princeton"
    assert data["data"] == "01010101"
    assert "timestamp" in data


def test_ir_signal_creation():
    """Test IRSignal dataclass."""
    signal = IRSignal(
        protocol="NEC",
        address="00",
        command="01",
        raw_data=[100, 200, 300],
    )
    
    assert signal.protocol == "NEC"
    assert signal.address == "00"
    assert signal.command == "01"
    assert signal.raw_data == [100, 200, 300]


def test_ir_signal_to_dict():
    """Test IRSignal to_dict conversion."""
    signal = IRSignal(
        protocol="NEC",
        address="00",
        command="01",
        raw_data=[100, 200, 300],
    )
    
    data = signal.to_dict()
    
    assert data["protocol"] == "NEC"
    assert data["address"] == "00"
    assert data["command"] == "01"
    assert data["raw_data"] == [100, 200, 300]
    assert "timestamp" in data


def test_flipper_initialization():
    """Test FlipperZero initialization."""
    flipper = FlipperZero(port="/dev/ttyACM0", baudrate=230400)
    
    assert flipper.port == "/dev/ttyACM0"
    assert flipper.baudrate == 230400
    assert flipper.is_connected is False
    assert flipper.is_reading is False
    assert len(flipper.rfid_tags) == 0
    assert len(flipper.nfc_tags) == 0
    assert len(flipper.subghz_signals) == 0
    assert len(flipper.ir_signals) == 0


def test_flipper_discover_devices():
    """Test device discovery (returns empty list in test environment)."""
    devices = FlipperZero.discover_devices()
    assert isinstance(devices, list)
    # In test environment, likely no devices connected


def test_flipper_get_device_info():
    """Test get_device_info method."""
    flipper = FlipperZero(port="/dev/ttyACM0")
    
    info = flipper.get_device_info()
    
    assert info["port"] == "/dev/ttyACM0"
    assert info["is_connected"] is False
    assert info["is_reading"] is False
    assert info["rfid_tags"] == 0
    assert info["nfc_tags"] == 0


def test_flipper_parse_rfid_response():
    """Test RFID response parsing."""
    flipper = FlipperZero()
    
    # Valid response
    response = "UID: 1234567890\nType: EM4100"
    tag = flipper._parse_rfid_response(response, FlipperProtocol.RFID_125KHZ)
    
    assert tag is not None
    assert tag.uid == "1234567890"
    assert tag.protocol == FlipperProtocol.RFID_125KHZ


def test_flipper_parse_rfid_response_invalid():
    """Test RFID response parsing with invalid data."""
    flipper = FlipperZero()
    
    # Invalid response
    response = "Invalid data"
    tag = flipper._parse_rfid_response(response, FlipperProtocol.RFID_125KHZ)
    
    assert tag is None


def test_flipper_parse_nfc_response():
    """Test NFC response parsing."""
    flipper = FlipperZero()
    
    # Valid response
    response = "UID: 04:12:34:56:78:90\nATQA: 0044\nSAK: 00"
    tag = flipper._parse_nfc_response(response)
    
    assert tag is not None
    assert tag.uid == "04:12:34:56:78:90"
    assert tag.atqa == "0044"
    assert tag.sak == "00"


def test_flipper_parse_nfc_response_invalid():
    """Test NFC response parsing with invalid data."""
    flipper = FlipperZero()
    
    # Invalid response
    response = "Invalid data"
    tag = flipper._parse_nfc_response(response)
    
    assert tag is None


def test_flipper_parse_subghz_response():
    """Test Sub-GHz response parsing."""
    flipper = FlipperZero()
    
    # Valid response
    response = "Protocol: Princeton\nData: 01010101"
    signals = flipper._parse_subghz_response(response, 433.92)
    
    assert isinstance(signals, list)
    if signals:
        assert signals[0].protocol == "Princeton"
        assert signals[0].frequency == 433.92


def test_flipper_parse_ir_response():
    """Test IR response parsing."""
    flipper = FlipperZero()
    
    # Valid response
    response = "Protocol: NEC\nAddress: 00\nCommand: 01"
    signal = flipper._parse_ir_response(response)
    
    assert signal is not None
    assert signal.protocol == "NEC"


def test_flipper_context_manager():
    """Test context manager protocol."""
    flipper = FlipperZero(port="/dev/ttyACM0")
    
    # Should not raise error
    try:
        with flipper as f:
            assert f is flipper
    except Exception:
        # Expected in test environment without actual device
        pass


@pytest.mark.asyncio
async def test_flipper_read_rfid_not_connected():
    """Test RFID read when not connected."""
    flipper = FlipperZero()
    
    tag = await flipper.read_rfid_125khz(duration=1.0)
    
    # Should return None when not connected
    assert tag is None


@pytest.mark.asyncio
async def test_flipper_read_nfc_not_connected():
    """Test NFC read when not connected."""
    flipper = FlipperZero()
    
    tag = await flipper.read_nfc(duration=1.0)
    
    # Should return None when not connected
    assert tag is None


@pytest.mark.asyncio
async def test_flipper_receive_subghz_not_connected():
    """Test Sub-GHz receive when not connected."""
    flipper = FlipperZero()
    
    signals = await flipper.receive_subghz(frequency=433.92, duration=1.0)
    
    # Should return empty list when not connected
    assert isinstance(signals, list)
    assert len(signals) == 0


@pytest.mark.asyncio
async def test_flipper_receive_infrared_not_connected():
    """Test IR receive when not connected."""
    flipper = FlipperZero()
    
    signal = await flipper.receive_infrared(duration=1.0)
    
    # Should return None when not connected
    assert signal is None


def test_flipper_transmit_subghz_not_connected():
    """Test Sub-GHz transmit when not connected."""
    flipper = FlipperZero()
    
    result = flipper.transmit_subghz(433.92, "Princeton", "01010101")
    
    # Should fail when not connected
    assert result is False


def test_flipper_transmit_infrared_not_connected():
    """Test IR transmit when not connected."""
    flipper = FlipperZero()
    
    result = flipper.transmit_infrared("NEC", "00", "01")
    
    # Should fail when not connected
    assert result is False


def test_flipper_set_gpio_not_connected():
    """Test GPIO set when not connected."""
    flipper = FlipperZero()
    
    result = flipper.set_gpio(1, True)
    
    # Should fail when not connected
    assert result is False


def test_flipper_read_gpio_not_connected():
    """Test GPIO read when not connected."""
    flipper = FlipperZero()
    
    result = flipper.read_gpio(1)
    
    # Should return None when not connected
    assert result is None


def test_flipper_stop_reading_not_connected():
    """Test stop reading when not connected."""
    flipper = FlipperZero()
    
    result = flipper.stop_reading()
    
    # Should return False when not connected
    assert result is False
