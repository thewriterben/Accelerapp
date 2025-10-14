"""
BLE stack integration for Nordic nRF platforms.
Provides BLE service generation and SoftDevice configuration.
"""

from typing import Dict, Any, List


class BLEStack:
    """
    Bluetooth Low Energy stack integration for Nordic platforms.
    Generates BLE services, characteristics, and advertising configuration.
    """

    def __init__(self, variant: str = "s140"):
        """
        Initialize BLE stack.
        
        Args:
            variant: SoftDevice variant (s140 for nRF52, s340 for nRF53)
        """
        self.variant = variant
        self.services = []
        
    def generate_service(self, service_config: Dict[str, Any]) -> str:
        """
        Generate BLE service implementation.
        
        Args:
            service_config: Service configuration
            
        Returns:
            Generated C code
        """
        service_name = service_config.get("name", "custom_service")
        uuid = service_config.get("uuid", "0x1234")
        characteristics = service_config.get("characteristics", [])
        
        lines = [
            f"/* BLE {service_name} Service */",
            f'#include "ble_{service_name}.h"',
            '#include "ble_srv_common.h"',
            "",
            f"#define {service_name.upper()}_UUID {uuid}",
            "",
        ]
        
        # Generate characteristics
        for char in characteristics:
            char_name = char.get("name", "char")
            char_uuid = char.get("uuid", "0x1235")
            lines.extend([
                f"#define {char_name.upper()}_UUID {char_uuid}",
            ])
        
        lines.extend([
            "",
            f"uint32_t ble_{service_name}_init(ble_{service_name}_t * p_{service_name}) {{",
            "    uint32_t err_code;",
            "    ble_uuid_t ble_uuid;",
            "",
            "    /* Initialize service structure */",
            f"    p_{service_name}->conn_handle = BLE_CONN_HANDLE_INVALID;",
            "",
            "    /* Add service UUID */",
            f"    ble_uuid.type = p_{service_name}->uuid_type;",
            f"    ble_uuid.uuid = {service_name.upper()}_UUID;",
            "",
            f"    err_code = sd_ble_gatts_service_add(BLE_GATTS_SRVC_TYPE_PRIMARY,",
            f"                                         &ble_uuid,",
            f"                                         &p_{service_name}->service_handle);",
            "    VERIFY_SUCCESS(err_code);",
            "",
        ])
        
        # Add characteristics
        for char in characteristics:
            char_name = char.get("name", "char")
            lines.extend([
                f"    /* Add {char_name} characteristic */",
                f"    err_code = {char_name}_char_add(p_{service_name});",
                "    VERIFY_SUCCESS(err_code);",
                "",
            ])
        
        lines.extend([
            "    return NRF_SUCCESS;",
            "}",
            "",
        ])
        
        return "\n".join(lines)
    
    def generate_advertising(self, adv_config: Dict[str, Any]) -> str:
        """
        Generate BLE advertising configuration.
        
        Args:
            adv_config: Advertising configuration
            
        Returns:
            Generated C code
        """
        device_name = adv_config.get("device_name", "Nordic_Device")
        interval = adv_config.get("interval", 300)  # in units of 0.625ms
        timeout = adv_config.get("timeout", 180)  # seconds
        
        lines = [
            "/* BLE Advertising Configuration */",
            '#include "ble_advertising.h"',
            "",
            "static ble_advertising_t m_advertising;",
            "",
            "void advertising_init(void) {",
            "    uint32_t err_code;",
            "    ble_advertising_init_t init;",
            "",
            "    memset(&init, 0, sizeof(init));",
            "",
            f'    init.advdata.name_type = BLE_ADVDATA_FULL_NAME;',
            "    init.advdata.include_appearance = true;",
            "    init.advdata.flags = BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE;",
            "",
            "    init.config.ble_adv_fast_enabled = true;",
            f"    init.config.ble_adv_fast_interval = {interval};",
            f"    init.config.ble_adv_fast_timeout = {timeout};",
            "",
            "    init.evt_handler = on_adv_evt;",
            "",
            "    err_code = ble_advertising_init(&m_advertising, &init);",
            "    APP_ERROR_CHECK(err_code);",
            "}",
            "",
            "void advertising_start(void) {",
            "    uint32_t err_code = ble_advertising_start(&m_advertising, BLE_ADV_MODE_FAST);",
            "    APP_ERROR_CHECK(err_code);",
            "}",
            "",
        ]
        
        return "\n".join(lines)
    
    def generate_gap_params(self, gap_config: Dict[str, Any]) -> str:
        """
        Generate GAP parameters configuration.
        
        Args:
            gap_config: GAP configuration
            
        Returns:
            Generated C code
        """
        device_name = gap_config.get("device_name", "Nordic_Device")
        appearance = gap_config.get("appearance", "BLE_APPEARANCE_GENERIC_TAG")
        min_conn_interval = gap_config.get("min_conn_interval", 20)
        max_conn_interval = gap_config.get("max_conn_interval", 75)
        
        lines = [
            "/* GAP Parameters Configuration */",
            "void gap_params_init(void) {",
            "    uint32_t err_code;",
            "    ble_gap_conn_params_t gap_conn_params;",
            "    ble_gap_conn_sec_mode_t sec_mode;",
            "",
            "    BLE_GAP_CONN_SEC_MODE_SET_OPEN(&sec_mode);",
            "",
            f'    err_code = sd_ble_gap_device_name_set(&sec_mode,',
            f'                                           (const uint8_t *)"{device_name}",',
            f'                                           strlen("{device_name}"));',
            "    APP_ERROR_CHECK(err_code);",
            "",
            f"    err_code = sd_ble_gap_appearance_set({appearance});",
            "    APP_ERROR_CHECK(err_code);",
            "",
            "    memset(&gap_conn_params, 0, sizeof(gap_conn_params));",
            "",
            f"    gap_conn_params.min_conn_interval = MSEC_TO_UNITS({min_conn_interval}, UNIT_1_25_MS);",
            f"    gap_conn_params.max_conn_interval = MSEC_TO_UNITS({max_conn_interval}, UNIT_1_25_MS);",
            "    gap_conn_params.slave_latency = 0;",
            "    gap_conn_params.conn_sup_timeout = MSEC_TO_UNITS(4000, UNIT_10_MS);",
            "",
            "    err_code = sd_ble_gap_ppcp_set(&gap_conn_params);",
            "    APP_ERROR_CHECK(err_code);",
            "}",
            "",
        ]
        
        return "\n".join(lines)
    
    def generate_complete_ble_init(self, config: Dict[str, Any]) -> str:
        """
        Generate complete BLE stack initialization.
        
        Args:
            config: Complete BLE configuration
            
        Returns:
            Generated C code
        """
        lines = [
            "/* Complete BLE Stack Initialization */",
            '#include "nrf_sdh.h"',
            '#include "nrf_sdh_ble.h"',
            "",
            "void ble_stack_init(void) {",
            "    ret_code_t err_code;",
            "",
            "    /* Initialize SoftDevice */",
            "    err_code = nrf_sdh_enable_request();",
            "    APP_ERROR_CHECK(err_code);",
            "",
            "    /* Configure BLE stack */",
            "    uint32_t ram_start = 0;",
            "    err_code = nrf_sdh_ble_default_cfg_set(APP_BLE_CONN_CFG_TAG, &ram_start);",
            "    APP_ERROR_CHECK(err_code);",
            "",
            "    /* Enable BLE stack */",
            "    err_code = nrf_sdh_ble_enable(&ram_start);",
            "    APP_ERROR_CHECK(err_code);",
            "",
            "    /* Register BLE event handler */",
            "    NRF_SDH_BLE_OBSERVER(m_ble_observer, APP_BLE_OBSERVER_PRIO, ble_evt_handler, NULL);",
            "}",
            "",
        ]
        
        return "\n".join(lines)
