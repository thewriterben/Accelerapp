"""
STM32CubeMX integration for project generation.
Generates CubeMX-compatible project files and configurations.
"""

import json
from pathlib import Path
from typing import Any, Dict, List


class CubeMXIntegration:
    """
    Integration with STM32CubeMX for project generation.
    Generates .ioc files and project configurations.
    """

    def __init__(self):
        """Initialize CubeMX integration."""
        self.project_name = ""
        self.mcu_name = ""

    def generate_ioc_file(self, config: Dict[str, Any], output_path: Path) -> bool:
        """
        Generate STM32CubeMX .ioc configuration file.

        Args:
            config: Project configuration
            output_path: Output path for .ioc file

        Returns:
            True if successful
        """
        self.project_name = config.get("project_name", "STM32Project")
        self.mcu_name = config.get("mcu", "STM32F401RETx")

        ioc_content = self._build_ioc_content(config)

        output_path.write_text(ioc_content)
        return True

    def _build_ioc_content(self, config: Dict[str, Any]) -> str:
        """
        Build .ioc file content.

        Args:
            config: Project configuration

        Returns:
            IOC file content as string
        """
        lines = [
            "#MicroXplorer Configuration settings - do not modify",
            "File.Version=6",
            "KeepUserPlacement=false",
            f"Mcu.Family={self._get_mcu_family()}",
            "Mcu.IP0=NVIC",
            "Mcu.IP1=RCC",
            "Mcu.IPNb=2",
            f"Mcu.Name={self.mcu_name}",
            f"Mcu.Package={self._get_package()}",
            "Mcu.Pin0=PC13-ANTI_TAMP",
            "Mcu.Pin1=PA13",
            "Mcu.Pin2=PA14",
            "Mcu.PinsNb=3",
            "Mcu.ThirdPartyNb=0",
            "Mcu.UserConstants=",
            f"Mcu.UserName={self.mcu_name}",
            "ProjectManager.AskForMigrate=true",
            "ProjectManager.BackupPrevious=false",
            "ProjectManager.CompilerOptimize=6",
            "ProjectManager.ComputerToolchain=false",
            "ProjectManager.CoupleFile=false",
            "ProjectManager.CustomerFirmwarePackage=",
            "ProjectManager.DefaultFWLocation=true",
            "ProjectManager.DeletePrevious=true",
            f"ProjectManager.DeviceId={self.mcu_name}",
            "ProjectManager.FirmwarePackage=STM32Cube FW_F4 V1.27.0",
            "ProjectManager.FreePins=false",
            "ProjectManager.HalAssertFull=false",
            "ProjectManager.HeapSize=0x200",
            "ProjectManager.KeepUserCode=true",
            "ProjectManager.LastFirmware=true",
            "ProjectManager.LibraryCopy=1",
            "ProjectManager.MainLocation=Core/Src",
            "ProjectManager.NoMain=false",
            "ProjectManager.PreviousToolchain=",
            "ProjectManager.ProjectBuild=false",
            f"ProjectManager.ProjectFileName={self.project_name}.ioc",
            f"ProjectManager.ProjectName={self.project_name}",
            "ProjectManager.StackSize=0x400",
            "ProjectManager.TargetToolchain=STM32CubeIDE",
            "ProjectManager.ToolChainLocation=",
            "ProjectManager.UnderRoot=true",
            "ProjectManager.functionlistsort=1-MX_GPIO_Init-GPIO-false-HAL-true,2-SystemClock_Config-RCC-false-HAL-false",
        ]

        # Add peripheral configurations
        if config.get("peripherals"):
            for peripheral in config["peripherals"]:
                lines.extend(self._generate_peripheral_ioc(peripheral))

        return "\n".join(lines)

    def _get_mcu_family(self) -> str:
        """Get MCU family from MCU name."""
        if "F4" in self.mcu_name:
            return "STM32F4"
        elif "F7" in self.mcu_name:
            return "STM32F7"
        elif "H7" in self.mcu_name:
            return "STM32H7"
        elif "L4" in self.mcu_name:
            return "STM32L4"
        return "STM32F4"

    def _get_package(self) -> str:
        """Get MCU package from MCU name."""
        # Extract package from MCU name (simplified)
        if "LQFP64" in self.mcu_name or self.mcu_name.endswith("Rx"):
            return "LQFP64"
        elif "LQFP100" in self.mcu_name:
            return "LQFP100"
        return "LQFP64"

    def _generate_peripheral_ioc(self, peripheral: Dict[str, Any]) -> List[str]:
        """Generate IOC configuration for a peripheral."""
        lines = []
        ptype = peripheral.get("type", "gpio")

        if ptype == "uart":
            instance = peripheral.get("instance", "USART2")
            lines.extend(
                [
                    f"{instance}.BaudRate={peripheral.get('baudrate', 115200)}",
                    f"{instance}.IPParameters=BaudRate",
                    f"{instance}.Mode=MODE_TX_RX",
                ]
            )
        elif ptype == "i2c":
            instance = peripheral.get("instance", "I2C1")
            lines.extend(
                [
                    f"{instance}.ClockSpeed={peripheral.get('clock_speed', 100000)}",
                    f"{instance}.IPParameters=ClockSpeed",
                ]
            )

        return lines

    def generate_project_files(self, config: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """
        Generate complete STM32CubeIDE project structure.

        Args:
            config: Project configuration
            output_dir: Output directory

        Returns:
            Dictionary of generated files
        """
        files = {}

        # Create project structure
        (output_dir / "Core" / "Src").mkdir(parents=True, exist_ok=True)
        (output_dir / "Core" / "Inc").mkdir(parents=True, exist_ok=True)
        (output_dir / "Drivers").mkdir(parents=True, exist_ok=True)

        # Generate .project file
        project_file = output_dir / ".project"
        project_content = self._generate_eclipse_project(config)
        project_file.write_text(project_content)
        files[".project"] = str(project_file)

        # Generate .cproject file
        cproject_file = output_dir / ".cproject"
        cproject_content = self._generate_eclipse_cproject(config)
        cproject_file.write_text(cproject_content)
        files[".cproject"] = str(cproject_file)

        # Generate .ioc file
        ioc_file = output_dir / f"{config.get('project_name', 'project')}.ioc"
        self.generate_ioc_file(config, ioc_file)
        files[".ioc"] = str(ioc_file)

        return files

    def _generate_eclipse_project(self, config: Dict[str, Any]) -> str:
        """Generate Eclipse .project file."""
        project_name = config.get("project_name", "STM32Project")
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>{project_name}</name>
    <comment></comment>
    <projects>
    </projects>
    <buildSpec>
        <buildCommand>
            <name>org.eclipse.cdt.managedbuilder.core.genmakebuilder</name>
            <triggers>clean,full,incremental,</triggers>
            <arguments>
            </arguments>
        </buildCommand>
        <buildCommand>
            <name>org.eclipse.cdt.managedbuilder.core.ScannerConfigBuilder</name>
            <triggers>full,incremental,</triggers>
            <arguments>
            </arguments>
        </buildCommand>
    </buildSpec>
    <natures>
        <nature>org.eclipse.cdt.core.cnature</nature>
        <nature>org.eclipse.cdt.managedbuilder.core.managedBuildNature</nature>
        <nature>org.eclipse.cdt.managedbuilder.core.ScannerConfigNature</nature>
    </natures>
</projectDescription>
"""

    def _generate_eclipse_cproject(self, config: Dict[str, Any]) -> str:
        """Generate Eclipse .cproject file (simplified)."""
        return """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?fileVersion 4.0.0?>
<cproject storage_type_id="org.eclipse.cdt.core.XmlProjectDescriptionStorage">
    <storageModule moduleId="org.eclipse.cdt.core.settings">
        <cconfiguration id="com.st.stm32cube.ide.mcu.gnu.managedbuild.config.exe.debug">
            <storageModule buildSystemId="org.eclipse.cdt.managedbuilder.core.configurationDataProvider"
                           id="com.st.stm32cube.ide.mcu.gnu.managedbuild.config.exe.debug"
                           moduleId="org.eclipse.cdt.core.settings"
                           name="Debug">
                <externalSettings/>
                <extensions>
                    <extension id="org.eclipse.cdt.core.ELF" point="org.eclipse.cdt.core.BinaryParser"/>
                    <extension id="org.eclipse.cdt.core.GASErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
                    <extension id="org.eclipse.cdt.core.GmakeErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
                    <extension id="org.eclipse.cdt.core.GLDErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
                    <extension id="org.eclipse.cdt.core.CWDLocator" point="org.eclipse.cdt.core.ErrorParser"/>
                    <extension id="org.eclipse.cdt.core.GCCErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
                </extensions>
            </storageModule>
        </cconfiguration>
    </storageModule>
</cproject>
"""
