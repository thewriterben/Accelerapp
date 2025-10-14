"""
STM32 HAL code generator.
Generates HAL-compatible initialization and driver code.
"""

from typing import Dict, Any, List
from pathlib import Path


class STM32HALGenerator:
    """
    Generator for STM32 HAL library code.
    Produces initialization code compatible with STM32Cube HAL drivers.
    """

    def __init__(self, series: str = "F4"):
        """
        Initialize HAL generator.
        
        Args:
            series: STM32 series (F4, H7, L4, etc.)
        """
        self.series = series
        
    def generate_gpio_init(self, gpio_config: Dict[str, Any]) -> str:
        """
        Generate GPIO initialization code.
        
        Args:
            gpio_config: GPIO configuration dictionary
            
        Returns:
            Generated C code
        """
        lines = [
            "/* GPIO Initialization */",
            "static void MX_GPIO_Init(void) {",
            "    GPIO_InitTypeDef GPIO_InitStruct = {0};",
            "",
            "    /* GPIO Ports Clock Enable */",
        ]
        
        # Enable required GPIO ports
        ports = gpio_config.get("ports", ["A", "B", "C"])
        for port in ports:
            lines.append(f"    __HAL_RCC_GPIO{port}_CLK_ENABLE();")
        
        lines.append("")
        
        # Configure each pin
        for pin_config in gpio_config.get("pins", []):
            port = pin_config.get("port", "A")
            pin = pin_config.get("pin", 0)
            mode = pin_config.get("mode", "OUTPUT_PP")
            pull = pin_config.get("pull", "NOPULL")
            speed = pin_config.get("speed", "FREQ_LOW")
            
            lines.extend([
                f"    /* Configure GPIO pin: P{port}{pin} */",
                f"    GPIO_InitStruct.Pin = GPIO_PIN_{pin};",
                f"    GPIO_InitStruct.Mode = GPIO_MODE_{mode};",
                f"    GPIO_InitStruct.Pull = GPIO_{pull};",
                f"    GPIO_InitStruct.Speed = GPIO_SPEED_{speed};",
                f"    HAL_GPIO_Init(GPIO{port}, &GPIO_InitStruct);",
                "",
            ])
        
        lines.append("}")
        return "\n".join(lines)
    
    def generate_uart_init(self, uart_config: Dict[str, Any]) -> str:
        """
        Generate UART initialization code.
        
        Args:
            uart_config: UART configuration dictionary
            
        Returns:
            Generated C code
        """
        instance = uart_config.get("instance", "USART2")
        baudrate = uart_config.get("baudrate", 115200)
        wordlength = uart_config.get("wordlength", "8B")
        stopbits = uart_config.get("stopbits", "1")
        parity = uart_config.get("parity", "NONE")
        
        lines = [
            f"/* {instance} Initialization */",
            f"static UART_HandleTypeDef huart{instance[-1]};",
            "",
            f"static void MX_{instance}_UART_Init(void) {{",
            f"    huart{instance[-1]}.Instance = {instance};",
            f"    huart{instance[-1]}.Init.BaudRate = {baudrate};",
            f"    huart{instance[-1]}.Init.WordLength = UART_WORDLENGTH_{wordlength};",
            f"    huart{instance[-1]}.Init.StopBits = UART_STOPBITS_{stopbits};",
            f"    huart{instance[-1]}.Init.Parity = UART_PARITY_{parity};",
            f"    huart{instance[-1]}.Init.Mode = UART_MODE_TX_RX;",
            f"    huart{instance[-1]}.Init.HwFlowCtl = UART_HWCONTROL_NONE;",
            f"    huart{instance[-1]}.Init.OverSampling = UART_OVERSAMPLING_16;",
            "",
            f"    if (HAL_UART_Init(&huart{instance[-1]}) != HAL_OK) {{",
            "        Error_Handler();",
            "    }",
            "}",
        ]
        return "\n".join(lines)
    
    def generate_i2c_init(self, i2c_config: Dict[str, Any]) -> str:
        """
        Generate I2C initialization code.
        
        Args:
            i2c_config: I2C configuration dictionary
            
        Returns:
            Generated C code
        """
        instance = i2c_config.get("instance", "I2C1")
        clock_speed = i2c_config.get("clock_speed", 100000)
        
        lines = [
            f"/* {instance} Initialization */",
            f"static I2C_HandleTypeDef hi2c{instance[-1]};",
            "",
            f"static void MX_{instance}_Init(void) {{",
            f"    hi2c{instance[-1]}.Instance = {instance};",
            f"    hi2c{instance[-1]}.Init.ClockSpeed = {clock_speed};",
            f"    hi2c{instance[-1]}.Init.DutyCycle = I2C_DUTYCYCLE_2;",
            f"    hi2c{instance[-1]}.Init.OwnAddress1 = 0;",
            f"    hi2c{instance[-1]}.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;",
            f"    hi2c{instance[-1]}.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;",
            f"    hi2c{instance[-1]}.Init.OwnAddress2 = 0;",
            f"    hi2c{instance[-1]}.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;",
            f"    hi2c{instance[-1]}.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;",
            "",
            f"    if (HAL_I2C_Init(&hi2c{instance[-1]}) != HAL_OK) {{",
            "        Error_Handler();",
            "    }",
            "}",
        ]
        return "\n".join(lines)
    
    def generate_spi_init(self, spi_config: Dict[str, Any]) -> str:
        """
        Generate SPI initialization code.
        
        Args:
            spi_config: SPI configuration dictionary
            
        Returns:
            Generated C code
        """
        instance = spi_config.get("instance", "SPI1")
        mode = spi_config.get("mode", "MASTER")
        direction = spi_config.get("direction", "2LINES")
        datasize = spi_config.get("datasize", "8BIT")
        prescaler = spi_config.get("prescaler", "256")
        
        lines = [
            f"/* {instance} Initialization */",
            f"static SPI_HandleTypeDef hspi{instance[-1]};",
            "",
            f"static void MX_{instance}_Init(void) {{",
            f"    hspi{instance[-1]}.Instance = {instance};",
            f"    hspi{instance[-1]}.Init.Mode = SPI_MODE_{mode};",
            f"    hspi{instance[-1]}.Init.Direction = SPI_DIRECTION_{direction};",
            f"    hspi{instance[-1]}.Init.DataSize = SPI_DATASIZE_{datasize};",
            f"    hspi{instance[-1]}.Init.CLKPolarity = SPI_POLARITY_LOW;",
            f"    hspi{instance[-1]}.Init.CLKPhase = SPI_PHASE_1EDGE;",
            f"    hspi{instance[-1]}.Init.NSS = SPI_NSS_SOFT;",
            f"    hspi{instance[-1]}.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_{prescaler};",
            f"    hspi{instance[-1]}.Init.FirstBit = SPI_FIRSTBIT_MSB;",
            f"    hspi{instance[-1]}.Init.TIMode = SPI_TIMODE_DISABLE;",
            f"    hspi{instance[-1]}.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;",
            "",
            f"    if (HAL_SPI_Init(&hspi{instance[-1]}) != HAL_OK) {{",
            "        Error_Handler();",
            "    }",
            "}",
        ]
        return "\n".join(lines)
    
    def generate_timer_init(self, timer_config: Dict[str, Any]) -> str:
        """
        Generate Timer initialization code.
        
        Args:
            timer_config: Timer configuration dictionary
            
        Returns:
            Generated C code
        """
        instance = timer_config.get("instance", "TIM2")
        prescaler = timer_config.get("prescaler", 84)
        period = timer_config.get("period", 1000)
        
        lines = [
            f"/* {instance} Initialization */",
            f"static TIM_HandleTypeDef htim{instance[-1]};",
            "",
            f"static void MX_{instance}_Init(void) {{",
            f"    TIM_ClockConfigTypeDef sClockSourceConfig = {{0}};",
            f"    TIM_MasterConfigTypeDef sMasterConfig = {{0}};",
            "",
            f"    htim{instance[-1]}.Instance = {instance};",
            f"    htim{instance[-1]}.Init.Prescaler = {prescaler} - 1;",
            f"    htim{instance[-1]}.Init.CounterMode = TIM_COUNTERMODE_UP;",
            f"    htim{instance[-1]}.Init.Period = {period} - 1;",
            f"    htim{instance[-1]}.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;",
            "",
            f"    if (HAL_TIM_Base_Init(&htim{instance[-1]}) != HAL_OK) {{",
            "        Error_Handler();",
            "    }",
            "",
            "    sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;",
            f"    if (HAL_TIM_ConfigClockSource(&htim{instance[-1]}, &sClockSourceConfig) != HAL_OK) {{",
            "        Error_Handler();",
            "    }",
            "}",
        ]
        return "\n".join(lines)
    
    def generate_adc_init(self, adc_config: Dict[str, Any]) -> str:
        """
        Generate ADC initialization code with DMA support.
        
        Args:
            adc_config: ADC configuration dictionary
            
        Returns:
            Generated C code
        """
        instance = adc_config.get("instance", "ADC1")
        resolution = adc_config.get("resolution", "12BIT")
        use_dma = adc_config.get("use_dma", False)
        
        lines = [
            f"/* {instance} Initialization */",
            f"static ADC_HandleTypeDef hadc{instance[-1]};",
        ]
        
        if use_dma:
            lines.append(f"static DMA_HandleTypeDef hdma_adc{instance[-1]};")
        
        lines.extend([
            "",
            f"static void MX_{instance}_Init(void) {{",
            f"    ADC_ChannelConfTypeDef sConfig = {{0}};",
            "",
            f"    hadc{instance[-1]}.Instance = {instance};",
            f"    hadc{instance[-1]}.Init.Resolution = ADC_RESOLUTION_{resolution};",
            f"    hadc{instance[-1]}.Init.ScanConvMode = DISABLE;",
            f"    hadc{instance[-1]}.Init.ContinuousConvMode = ENABLE;",
            f"    hadc{instance[-1]}.Init.DiscontinuousConvMode = DISABLE;",
            f"    hadc{instance[-1]}.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;",
            f"    hadc{instance[-1]}.Init.DataAlign = ADC_DATAALIGN_RIGHT;",
            f"    hadc{instance[-1]}.Init.NbrOfConversion = 1;",
        ])
        
        if use_dma:
            lines.append(f"    hadc{instance[-1]}.Init.DMAContinuousRequests = ENABLE;")
        
        lines.extend([
            "",
            f"    if (HAL_ADC_Init(&hadc{instance[-1]}) != HAL_OK) {{",
            "        Error_Handler();",
            "    }",
            "}",
        ])
        return "\n".join(lines)
    
    def generate_system_init(self, config: Dict[str, Any]) -> str:
        """
        Generate complete system initialization code.
        
        Args:
            config: Complete system configuration
            
        Returns:
            Generated C code
        """
        lines = [
            "/* System initialization */",
            '#include "main.h"',
            "",
            "void SystemInit(void) {",
            "    /* FPU settings */",
            "    #if (__FPU_PRESENT == 1) && (__FPU_USED == 1)",
            "        SCB->CPACR |= ((3UL << 10*2)|(3UL << 11*2));",
            "    #endif",
            "",
            "    /* Reset the RCC clock configuration to the default reset state */",
            "    RCC->CR |= RCC_CR_HSION;",
            "    RCC->CFGR = 0x00000000;",
            "",
            "    /* Configure peripherals */",
        ]
        
        if config.get("gpio"):
            lines.append("    MX_GPIO_Init();")
        if config.get("uart"):
            lines.append("    MX_USART2_UART_Init();")
        if config.get("i2c"):
            lines.append("    MX_I2C1_Init();")
        if config.get("spi"):
            lines.append("    MX_SPI1_Init();")
        if config.get("timer"):
            lines.append("    MX_TIM2_Init();")
        if config.get("adc"):
            lines.append("    MX_ADC1_Init();")
        
        lines.append("}")
        return "\n".join(lines)
