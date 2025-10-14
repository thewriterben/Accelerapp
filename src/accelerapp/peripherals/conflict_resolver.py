"""
Peripheral conflict detection and resolution system.
Detects pin conflicts and suggests alternative configurations.
"""

from typing import Dict, Any, List, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PinAssignment:
    """Represents a pin assignment for a peripheral."""
    peripheral_id: str
    peripheral_type: str
    pin_number: int
    pin_function: str  # e.g., "SPI_MOSI", "GPIO_OUTPUT", "I2C_SDA"
    alternate_function: Optional[int] = None  # AF number for advanced MCUs


class PeripheralConflictResolver:
    """
    Advanced peripheral conflict detection and resolution.
    Provides intelligent pin mapping and alternative suggestions.
    """

    def __init__(self, platform: str = "stm32"):
        """
        Initialize conflict resolver.
        
        Args:
            platform: Target platform for platform-specific resolution
        """
        self.platform = platform
        self.pin_assignments: Dict[int, List[PinAssignment]] = {}
        self.peripheral_instances: Dict[str, str] = {}  # peripheral_id -> type
        
    def add_peripheral(self, peripheral_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Add a peripheral and check for conflicts.
        
        Args:
            peripheral_config: Peripheral configuration
            
        Returns:
            Tuple of (success, conflicts/warnings)
        """
        peripheral_id = peripheral_config.get("id", f"periph_{len(self.peripheral_instances)}")
        peripheral_type = peripheral_config.get("type", "unknown")
        pins = peripheral_config.get("pins", [])
        
        conflicts = []
        
        # Check each pin for conflicts
        for pin_info in pins:
            pin_number = pin_info.get("pin")
            pin_function = pin_info.get("function", "GPIO")
            
            if pin_number in self.pin_assignments:
                existing = self.pin_assignments[pin_number]
                for existing_assignment in existing:
                    # Check if this is a real conflict
                    if not self._is_compatible(existing_assignment, pin_function):
                        conflicts.append(
                            f"Pin {pin_number} conflict: {peripheral_id}({pin_function}) vs "
                            f"{existing_assignment.peripheral_id}({existing_assignment.pin_function})"
                        )
            
            # Add the assignment
            assignment = PinAssignment(
                peripheral_id=peripheral_id,
                peripheral_type=peripheral_type,
                pin_number=pin_number,
                pin_function=pin_function,
                alternate_function=pin_info.get("af")
            )
            
            if pin_number not in self.pin_assignments:
                self.pin_assignments[pin_number] = []
            self.pin_assignments[pin_number].append(assignment)
        
        self.peripheral_instances[peripheral_id] = peripheral_type
        
        return len(conflicts) == 0, conflicts
    
    def _is_compatible(self, existing: PinAssignment, new_function: str) -> bool:
        """
        Check if two pin assignments are compatible.
        
        Args:
            existing: Existing pin assignment
            new_function: New pin function
            
        Returns:
            True if compatible (e.g., both are inputs)
        """
        # Some pin functions can coexist (e.g., multiple inputs)
        input_functions = {"GPIO_INPUT", "ADC_INPUT", "ANALOG_INPUT"}
        
        if existing.pin_function in input_functions and new_function in input_functions:
            # Multiple inputs on same pin might be OK with multiplexing
            return True
        
        return False
    
    def suggest_alternatives(self, peripheral_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest alternative pin configurations when conflicts are detected.
        
        Args:
            peripheral_config: Conflicting peripheral configuration
            
        Returns:
            List of alternative configurations
        """
        peripheral_type = peripheral_config.get("type")
        alternatives = []
        
        # Platform-specific alternative suggestions
        if self.platform in ["stm32", "stm32f4", "stm32h7"]:
            alternatives = self._suggest_stm32_alternatives(peripheral_config)
        elif self.platform in ["nrf52", "nrf53"]:
            alternatives = self._suggest_nrf_alternatives(peripheral_config)
        elif self.platform == "esp32":
            alternatives = self._suggest_esp32_alternatives(peripheral_config)
        
        return alternatives
    
    def _suggest_stm32_alternatives(self, peripheral_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest STM32-specific alternative pin configurations."""
        peripheral_type = peripheral_config.get("type")
        alternatives = []
        
        # STM32 has multiple alternate functions per peripheral
        if peripheral_type == "uart":
            alternatives.extend([
                {
                    "instance": "USART1",
                    "pins": [{"tx": "PA9", "rx": "PA10", "af": 7}],
                    "description": "USART1 on PA9/PA10 (AF7)"
                },
                {
                    "instance": "USART1",
                    "pins": [{"tx": "PB6", "rx": "PB7", "af": 7}],
                    "description": "USART1 on PB6/PB7 (AF7)"
                },
                {
                    "instance": "USART2",
                    "pins": [{"tx": "PA2", "rx": "PA3", "af": 7}],
                    "description": "USART2 on PA2/PA3 (AF7)"
                },
            ])
        elif peripheral_type == "i2c":
            alternatives.extend([
                {
                    "instance": "I2C1",
                    "pins": [{"scl": "PB6", "sda": "PB7", "af": 4}],
                    "description": "I2C1 on PB6/PB7 (AF4)"
                },
                {
                    "instance": "I2C1",
                    "pins": [{"scl": "PB8", "sda": "PB9", "af": 4}],
                    "description": "I2C1 on PB8/PB9 (AF4)"
                },
            ])
        elif peripheral_type == "spi":
            alternatives.extend([
                {
                    "instance": "SPI1",
                    "pins": [{"sck": "PA5", "miso": "PA6", "mosi": "PA7", "af": 5}],
                    "description": "SPI1 on PA5/PA6/PA7 (AF5)"
                },
                {
                    "instance": "SPI1",
                    "pins": [{"sck": "PB3", "miso": "PB4", "mosi": "PB5", "af": 5}],
                    "description": "SPI1 on PB3/PB4/PB5 (AF5)"
                },
            ])
        
        return alternatives
    
    def _suggest_nrf_alternatives(self, peripheral_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest nRF-specific alternative pin configurations."""
        # nRF has flexible pin mapping - almost any GPIO can be used
        alternatives = [
            {
                "description": "nRF platforms support flexible pin mapping - any available GPIO can be used",
                "pins": "P0.00-P0.31 (nRF52) or P0.00-P1.15 (nRF53)"
            }
        ]
        return alternatives
    
    def _suggest_esp32_alternatives(self, peripheral_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest ESP32-specific alternative pin configurations."""
        alternatives = [
            {
                "description": "ESP32 has flexible IO MUX - most peripherals can use various pins",
                "note": "Avoid GPIO 6-11 (connected to flash) and strapping pins (0, 2, 5, 12, 15)"
            }
        ]
        return alternatives
    
    def get_conflict_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive conflict report.
        
        Returns:
            Conflict analysis report
        """
        report = {
            "total_peripherals": len(self.peripheral_instances),
            "total_pins_used": len(self.pin_assignments),
            "conflicts": [],
            "warnings": [],
            "pin_utilization": {}
        }
        
        # Analyze each pin
        for pin_num, assignments in self.pin_assignments.items():
            if len(assignments) > 1:
                # Multiple assignments on same pin
                incompatible = []
                for i, assign1 in enumerate(assignments):
                    for assign2 in assignments[i+1:]:
                        if not self._is_compatible(assign1, assign2.pin_function):
                            incompatible.append((assign1, assign2))
                
                if incompatible:
                    for assign1, assign2 in incompatible:
                        report["conflicts"].append({
                            "pin": pin_num,
                            "peripheral1": assign1.peripheral_id,
                            "function1": assign1.pin_function,
                            "peripheral2": assign2.peripheral_id,
                            "function2": assign2.pin_function,
                        })
                else:
                    report["warnings"].append({
                        "pin": pin_num,
                        "message": f"Multiple compatible functions on pin {pin_num}",
                        "functions": [a.pin_function for a in assignments]
                    })
            
            report["pin_utilization"][pin_num] = {
                "count": len(assignments),
                "peripherals": [a.peripheral_id for a in assignments]
            }
        
        return report
    
    def optimize_pin_mapping(self) -> Dict[str, Any]:
        """
        Optimize pin mapping to minimize conflicts.
        
        Returns:
            Optimized pin mapping suggestions
        """
        # This is a placeholder for a more sophisticated optimization algorithm
        # Could use constraint satisfaction or genetic algorithms for complex cases
        
        optimization = {
            "status": "analyzed",
            "suggestions": [],
            "conflicts_resolved": 0
        }
        
        report = self.get_conflict_report()
        
        for conflict in report["conflicts"]:
            # For each conflict, suggest moving one peripheral to alternative pins
            peripheral_id = conflict["peripheral1"]
            peripheral_type = self.peripheral_instances.get(peripheral_id)
            
            if peripheral_type:
                alternatives = self.suggest_alternatives({
                    "id": peripheral_id,
                    "type": peripheral_type
                })
                
                if alternatives:
                    optimization["suggestions"].append({
                        "conflict": conflict,
                        "alternatives": alternatives
                    })
        
        return optimization
