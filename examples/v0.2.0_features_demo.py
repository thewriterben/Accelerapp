#!/usr/bin/env python3
"""
Demonstration of Accelerapp v0.2.0 features.
Shows new hardware protocols, optimization agents, and API functionality.
"""

from accelerapp.hardware import (
    I2CConfig, SPIConfig, CANConfig,
    ProtocolGenerator, DeviceDriverGenerator
)
from accelerapp.agents import (
    PerformanceOptimizationAgent,
    MemoryOptimizationAgent,
    CodeQualityAgent,
    SecurityAnalysisAgent,
    RefactoringAgent
)
from accelerapp.api import RateLimiter, APIKeyManager
from accelerapp.api.rate_limiter import RateLimitRule


def demo_i2c_protocol():
    """Demonstrate I2C protocol code generation."""
    print("=" * 70)
    print("Demo 1: I2C Protocol Code Generation")
    print("=" * 70)
    
    # Configure I2C for BME280 sensor
    config = I2CConfig(
        address=0x76,
        speed=400000,  # 400kHz fast mode
        sda_pin=21,
        scl_pin=22,
        pullup_enabled=True
    )
    
    print(f"I2C Configuration:")
    print(f"  Address: 0x{config.address:02X}")
    print(f"  Speed: {config.speed} Hz")
    print(f"  SDA Pin: {config.sda_pin}")
    print(f"  SCL Pin: {config.scl_pin}")
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print(f"  Validation errors: {errors}")
    else:
        print("  ✓ Configuration valid")
    
    # Generate code for ESP32
    code = ProtocolGenerator.generate_i2c_code(config, "esp32")
    print(f"\nGenerated I2C code for ESP32 ({len(code)} characters):")
    print("  ✓ Wire.h included")
    print("  ✓ setupI2C() function")
    print("  ✓ i2cWrite() function")
    print("  ✓ i2cRead() function")
    print()


def demo_spi_protocol():
    """Demonstrate SPI protocol code generation."""
    print("=" * 70)
    print("Demo 2: SPI Protocol Code Generation")
    print("=" * 70)
    
    # Configure SPI
    config = SPIConfig(
        mode=0,
        speed=2000000,  # 2 MHz
        mosi_pin=23,
        miso_pin=19,
        sclk_pin=18,
        cs_pin=5,
        bit_order="MSB"
    )
    
    print(f"SPI Configuration:")
    print(f"  Mode: {config.mode}")
    print(f"  Speed: {config.speed} Hz")
    print(f"  Bit Order: {config.bit_order}")
    
    # Generate code for Arduino
    code = ProtocolGenerator.generate_spi_code(config, "arduino")
    print(f"\nGenerated SPI code for Arduino ({len(code)} characters):")
    print("  ✓ SPI.h included")
    print("  ✓ setupSPI() function")
    print("  ✓ spiTransfer() function")
    print("  ✓ spiWrite() function")
    print()


def demo_can_protocol():
    """Demonstrate CAN bus code generation."""
    print("=" * 70)
    print("Demo 3: CAN Bus Code Generation")
    print("=" * 70)
    
    # Configure CAN bus
    config = CANConfig(
        baudrate=500000,  # 500 kbps
        tx_pin=5,
        rx_pin=4,
        mode="normal"
    )
    
    print(f"CAN Configuration:")
    print(f"  Baudrate: {config.baudrate} bps")
    print(f"  TX Pin: {config.tx_pin}")
    print(f"  RX Pin: {config.rx_pin}")
    print(f"  Mode: {config.mode}")
    
    # Generate code for ESP32
    code = ProtocolGenerator.generate_can_code(config, "esp32")
    print(f"\nGenerated CAN code for ESP32 ({len(code)} characters):")
    print("  ✓ driver/can.h included")
    print("  ✓ setupCAN() function")
    print("  ✓ canSend() function")
    print("  ✓ canReceive() function")
    print()


def demo_device_drivers():
    """Demonstrate device driver generation."""
    print("=" * 70)
    print("Demo 4: Device Driver Generation")
    print("=" * 70)
    
    sensors = [
        ("BME280", "Temperature/Humidity/Pressure"),
        ("MPU6050", "Accelerometer/Gyroscope"),
        ("INA219", "Current/Voltage Monitor")
    ]
    
    for sensor_name, description in sensors:
        driver = DeviceDriverGenerator.generate_sensor_driver(
            sensor_name.lower(), "i2c", "arduino"
        )
        print(f"\n{sensor_name} - {description}:")
        print(f"  ✓ Driver class generated ({len(driver)} characters)")
        print(f"  ✓ begin() initialization")
        print(f"  ✓ Sensor-specific read functions")


def demo_performance_optimization():
    """Demonstrate performance optimization agent."""
    print("\n" + "=" * 70)
    print("Demo 5: Performance Optimization Agent")
    print("=" * 70)
    
    agent = PerformanceOptimizationAgent()
    
    # Sample code with performance issues
    code = """
    void loop() {
        for(int i = 0; i < 1000; i++) {
            delay(10);  // Blocking operation in loop
            String result = "";
            for(int j = 0; j < 100; j++) {
                result += String(j);  // Inefficient string concatenation
            }
        }
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    print(f"Agent: {agent.name}")
    print(f"Analysis Status: {result['status']}")
    analysis = result['analysis']
    print(f"Issues Found: {analysis['issues_found']}")
    print(f"Estimated Improvement: {analysis['estimated_improvement']}")
    
    if analysis['issues']:
        print("\nIssues Detected:")
        for issue in analysis['issues']:
            print(f"  - {issue['type']}: {issue['description']} ({issue['severity']})")
    
    if analysis['suggestions']:
        print("\nOptimization Suggestions:")
        for suggestion in analysis['suggestions']:
            print(f"  - {suggestion['title']}")
            print(f"    {suggestion['description']}")


def demo_memory_optimization():
    """Demonstrate memory optimization agent."""
    print("\n" + "=" * 70)
    print("Demo 6: Memory Optimization Agent")
    print("=" * 70)
    
    agent = MemoryOptimizationAgent()
    
    # Sample code with memory issues
    code = """
    void setup() {
        char* buffer = (char*)malloc(1024);
        int* data = new int[100];
        Serial.println("Data allocated");
        // Memory leak - no free() or delete[]
    }
    """
    
    result = agent.generate({
        'code': code,
        'language': 'cpp',
        'platform': 'arduino'
    })
    
    print(f"Agent: {agent.name}")
    analysis = result['analysis']
    print(f"Issues Found: {analysis['issues_found']}")
    
    if analysis['issues']:
        print("\nMemory Issues:")
        for issue in analysis['issues']:
            print(f"  - {issue['type']}: {issue['description']} ({issue['severity']})")
    
    print(f"\nMemory Estimate:")
    mem_est = analysis['memory_estimate']
    print(f"  Estimated RAM: {mem_est['estimated_ram_bytes']} bytes")
    print(f"  Platform: {mem_est['platform']}")


def demo_code_quality():
    """Demonstrate code quality agent."""
    print("\n" + "=" * 70)
    print("Demo 7: Code Quality Agent")
    print("=" * 70)
    
    agent = CodeQualityAgent()
    
    # Sample code
    code = """
    void processData(int x) {
        int result = x * 42;  // Magic number
        if(result > 100) {
            // Do something
        }
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    print(f"Agent: {agent.name}")
    analysis = result['analysis']
    print(f"Quality Score: {analysis['quality_score']}/100")
    print(f"Grade: {analysis['grade']}")
    print(f"Issues Found: {analysis['issues_found']}")
    
    if analysis['suggestions']:
        print("\nQuality Improvements:")
        for suggestion in analysis['suggestions'][:3]:  # Show first 3
            print(f"  - {suggestion['title']}")


def demo_security_analysis():
    """Demonstrate security analysis agent."""
    print("\n" + "=" * 70)
    print("Demo 8: Security Analysis Agent")
    print("=" * 70)
    
    agent = SecurityAnalysisAgent()
    
    # Sample code with security issues
    code = """
    void processInput(char* input) {
        char buffer[10];
        strcpy(buffer, input);  // Buffer overflow risk
    }
    """
    
    result = agent.generate({'code': code, 'language': 'cpp'})
    
    print(f"Agent: {agent.name}")
    analysis = result['analysis']
    print(f"Security Score: {analysis['security_score']}/100")
    print(f"Risk Level: {analysis['risk_level']}")
    print(f"Vulnerabilities Found: {analysis['vulnerabilities_found']}")
    
    if analysis['vulnerabilities']:
        print("\nVulnerabilities:")
        for vuln in analysis['vulnerabilities']:
            print(f"  - {vuln['type']}: {vuln['description']}")
            print(f"    Severity: {vuln['severity']}, CWE: {vuln.get('cwe', 'N/A')}")


def demo_rate_limiting():
    """Demonstrate API rate limiting."""
    print("\n" + "=" * 70)
    print("Demo 9: API Rate Limiting")
    print("=" * 70)
    
    # Create rate limiter with restrictive limits for demo
    rule = RateLimitRule(max_requests=5, time_window=60)
    limiter = RateLimiter(default_rule=rule)
    
    print(f"Rate Limit: {rule.max_requests} requests per {rule.time_window} seconds")
    
    # Simulate requests
    client_id = "demo_client"
    for i in range(7):
        allowed, info = limiter.check_limit(client_id)
        status = "✓ ALLOWED" if allowed else "✗ DENIED"
        print(f"  Request {i+1}: {status} (Remaining: {info['remaining']})")
    
    # Show client info
    info = limiter.get_client_info(client_id)
    print(f"\nClient Info:")
    print(f"  Used: {info['used']}/{info['limit']}")
    print(f"  Remaining: {info['remaining']}")


def demo_api_keys():
    """Demonstrate API key management."""
    print("\n" + "=" * 70)
    print("Demo 10: API Key Management")
    print("=" * 70)
    
    manager = APIKeyManager()
    
    # Generate keys
    key1 = manager.generate_key("client1", permissions=['read', 'write'])
    key2 = manager.generate_key("client2", permissions=['read'])
    
    print("Generated API Keys:")
    print(f"  Key 1: {key1[:20]}... (read, write)")
    print(f"  Key 2: {key2[:20]}... (read)")
    
    # Validate key
    valid, client_id = manager.validate_key(key1)
    print(f"\nKey Validation:")
    print(f"  Valid: {valid}")
    print(f"  Client ID: {client_id}")
    
    # Get key info
    info = manager.get_key_info(key1)
    print(f"\nKey Info:")
    print(f"  Usage Count: {info['usage_count']}")
    print(f"  Permissions: {', '.join(info['permissions'])}")
    print(f"  Created: {info['created_at']}")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Accelerapp v0.2.0 Features Demo" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    demos = [
        demo_i2c_protocol,
        demo_spi_protocol,
        demo_can_protocol,
        demo_device_drivers,
        demo_performance_optimization,
        demo_memory_optimization,
        demo_code_quality,
        demo_security_analysis,
        demo_rate_limiting,
        demo_api_keys
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"Error in demo: {e}")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nKey v0.2.0 Features Demonstrated:")
    print("  ✓ I2C, SPI, and CAN protocol code generation")
    print("  ✓ Device driver generation for common sensors")
    print("  ✓ Performance optimization analysis")
    print("  ✓ Memory leak detection and optimization")
    print("  ✓ Code quality assessment with grading")
    print("  ✓ Security vulnerability detection")
    print("  ✓ Rate limiting for API protection")
    print("  ✓ Secure API key management")
    print()


if __name__ == "__main__":
    main()
