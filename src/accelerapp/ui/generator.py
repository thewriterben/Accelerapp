"""
UI generator for hardware control interfaces.
"""

from typing import Dict, Any
from pathlib import Path


class UIGenerator:
    """
    Generates user interfaces for hardware control.
    Supports web-based (React, Vue) and native (Electron) UIs.
    """

    def __init__(self, hardware_spec: Dict[str, Any]):
        """
        Initialize UI generator.
        
        Args:
            hardware_spec: Hardware specification dictionary
        """
        self.hardware_spec = hardware_spec
        self.framework = hardware_spec.get('ui_framework', 'react')

    def generate(self, output_dir: Path) -> Dict[str, Any]:
        """
        Generate UI based on hardware specification.
        
        Args:
            output_dir: Directory to write generated UI
            
        Returns:
            Dictionary with generation results
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.framework == 'react':
            return self._generate_react_ui(output_dir)
        elif self.framework == 'vue':
            return self._generate_vue_ui(output_dir)
        elif self.framework == 'html':
            return self._generate_html_ui(output_dir)
        else:
            return {
                'status': 'error',
                'error': f'Unsupported framework: {self.framework}'
            }

    def _generate_react_ui(self, output_dir: Path) -> Dict[str, Any]:
        """Generate React-based UI."""
        device_name = self.hardware_spec.get('device_name', 'Device')
        
        # Generate main App component
        app_code = [
            "import React, { useState, useEffect } from 'react';",
            "import './App.css';",
            "",
            f"function {device_name.replace(' ', '')}Control() {{",
            "  const [connected, setConnected] = useState(false);",
            "  const [status, setStatus] = useState('Disconnected');",
            "",
            "  const connect = async () => {",
            "    // Implement connection logic",
            "    setConnected(true);",
            "    setStatus('Connected');",
            "  };",
            "",
            "  const disconnect = () => {",
            "    setConnected(false);",
            "    setStatus('Disconnected');",
            "  };",
            "",
            "  return (",
            "    <div className='app-container'>",
            f"      <h1>{device_name} Control Panel</h1>",
            "      <div className='status-bar'>",
            "        <span>Status: {status}</span>",
            "        {!connected ? (",
            "          <button onClick={connect}>Connect</button>",
            "        ) : (",
            "          <button onClick={disconnect}>Disconnect</button>",
            "        )}",
            "      </div>",
            "",
            "      {connected && (",
            "        <div className='controls'>",
        ]
        
        # Add controls for each peripheral
        peripherals = self.hardware_spec.get('peripherals', [])
        for i, peripheral in enumerate(peripherals):
            p_type = peripheral['type']
            component_name = f"{p_type.capitalize()}Control"
            
            app_code.extend([
                f"          <{component_name} />",
            ])
        
        app_code.extend([
            "        </div>",
            "      )}",
            "    </div>",
            "  );",
            "}",
            ""
        ])
        
        # Add peripheral control components
        for peripheral in peripherals:
            p_type = peripheral['type']
            component_name = f"{p_type.capitalize()}Control"
            
            app_code.extend([
                f"function {component_name}() {{",
                "  const [value, setValue] = useState(0);",
                "",
                "  const handleChange = (e) => {",
                "    setValue(e.target.value);",
                "    // Send command to device",
                "  };",
                "",
                "  return (",
                "    <div className='peripheral-control'>",
                f"      <h3>{p_type.capitalize()}</h3>",
                "      <input",
                "        type='range'",
                "        min='0'",
                "        max='100'",
                "        value={value}",
                "        onChange={handleChange}",
                "      />",
                "      <span>{value}</span>",
                "    </div>",
                "  );",
                "}",
                ""
            ])
        
        app_code.extend([
            "export default " + device_name.replace(' ', '') + "Control;",
            ""
        ])
        
        app_file = output_dir / "App.jsx"
        app_file.write_text("\n".join(app_code))
        
        # Generate CSS
        css_code = [
            ".app-container {",
            "  max-width: 1200px;",
            "  margin: 0 auto;",
            "  padding: 20px;",
            "  font-family: Arial, sans-serif;",
            "}",
            "",
            "h1 {",
            "  color: #333;",
            "  text-align: center;",
            "}",
            "",
            ".status-bar {",
            "  display: flex;",
            "  justify-content: space-between;",
            "  align-items: center;",
            "  padding: 15px;",
            "  background: #f5f5f5;",
            "  border-radius: 8px;",
            "  margin-bottom: 20px;",
            "}",
            "",
            "button {",
            "  padding: 10px 20px;",
            "  background: #007bff;",
            "  color: white;",
            "  border: none;",
            "  border-radius: 4px;",
            "  cursor: pointer;",
            "}",
            "",
            "button:hover {",
            "  background: #0056b3;",
            "}",
            "",
            ".controls {",
            "  display: grid;",
            "  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));",
            "  gap: 20px;",
            "}",
            "",
            ".peripheral-control {",
            "  padding: 20px;",
            "  background: white;",
            "  border: 1px solid #ddd;",
            "  border-radius: 8px;",
            "  box-shadow: 0 2px 4px rgba(0,0,0,0.1);",
            "}",
            "",
            ".peripheral-control h3 {",
            "  margin-top: 0;",
            "  color: #555;",
            "}",
            "",
            "input[type='range'] {",
            "  width: 100%;",
            "  margin: 10px 0;",
            "}",
            ""
        ]
        
        css_file = output_dir / "App.css"
        css_file.write_text("\n".join(css_code))
        
        # Generate package.json
        package_json = {
            "name": f"{device_name.lower().replace(' ', '-')}-ui",
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            }
        }
        
        import json
        pkg_file = output_dir / "package.json"
        pkg_file.write_text(json.dumps(package_json, indent=2))
        
        # Generate index.html
        html_code = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "  <head>",
            "    <meta charset='utf-8' />",
            "    <meta name='viewport' content='width=device-width, initial-scale=1' />",
            f"    <title>{device_name} Control</title>",
            "  </head>",
            "  <body>",
            "    <noscript>You need to enable JavaScript to run this app.</noscript>",
            "    <div id='root'></div>",
            "  </body>",
            "</html>",
            ""
        ]
        
        html_file = output_dir / "index.html"
        html_file.write_text("\n".join(html_code))
        
        # Generate index.js
        index_code = [
            "import React from 'react';",
            "import ReactDOM from 'react-dom/client';",
            "import App from './App';",
            "",
            "const root = ReactDOM.createRoot(document.getElementById('root'));",
            "root.render(",
            "  <React.StrictMode>",
            "    <App />",
            "  </React.StrictMode>",
            ");",
            ""
        ]
        
        index_file = output_dir / "index.js"
        index_file.write_text("\n".join(index_code))
        
        # Generate README
        readme = [
            f"# {device_name} Control Interface",
            "",
            "Auto-generated React UI for hardware control.",
            "",
            "## Installation",
            "",
            "```bash",
            "npm install",
            "```",
            "",
            "## Usage",
            "",
            "```bash",
            "npm start",
            "```",
            "",
            "Then open http://localhost:3000",
            ""
        ]
        
        readme_file = output_dir / "README.md"
        readme_file.write_text("\n".join(readme))
        
        return {
            'status': 'success',
            'framework': 'react',
            'files_generated': [
                str(app_file),
                str(css_file),
                str(pkg_file),
                str(html_file),
                str(index_file),
                str(readme_file)
            ],
            'output_dir': str(output_dir)
        }

    def _generate_vue_ui(self, output_dir: Path) -> Dict[str, Any]:
        """Generate Vue-based UI."""
        # Placeholder for Vue implementation
        return {
            'status': 'success',
            'framework': 'vue',
            'files_generated': [],
            'output_dir': str(output_dir),
            'note': 'Vue UI generation not yet fully implemented'
        }

    def _generate_html_ui(self, output_dir: Path) -> Dict[str, Any]:
        """Generate simple HTML/JavaScript UI."""
        device_name = self.hardware_spec.get('device_name', 'Device')
        
        html_code = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>{device_name} Control</title>",
            "    <style>",
            "        body {",
            "            font-family: Arial, sans-serif;",
            "            max-width: 1200px;",
            "            margin: 0 auto;",
            "            padding: 20px;",
            "        }",
            "        .control-panel {",
            "            border: 1px solid #ddd;",
            "            padding: 20px;",
            "            margin: 10px 0;",
            "            border-radius: 8px;",
            "        }",
            "        button {",
            "            padding: 10px 20px;",
            "            margin: 5px;",
            "            cursor: pointer;",
            "        }",
            "    </style>",
            "</head>",
            "<body>",
            f"    <h1>{device_name} Control Panel</h1>",
            "    <div class='control-panel'>",
            "        <h2>Connection</h2>",
            "        <button id='connectBtn'>Connect</button>",
            "        <button id='disconnectBtn'>Disconnect</button>",
            "        <p>Status: <span id='status'>Disconnected</span></p>",
            "    </div>",
        ]
        
        # Add controls for peripherals
        peripherals = self.hardware_spec.get('peripherals', [])
        for peripheral in peripherals:
            p_type = peripheral['type']
            html_code.extend([
                "    <div class='control-panel'>",
                f"        <h2>{p_type.capitalize()}</h2>",
                f"        <button onclick=\"sendCommand('{p_type}', 'on')\">Turn On</button>",
                f"        <button onclick=\"sendCommand('{p_type}', 'off')\">Turn Off</button>",
                "    </div>",
            ])
        
        html_code.extend([
            "    <script>",
            "        let connected = false;",
            "",
            "        document.getElementById('connectBtn').addEventListener('click', () => {",
            "            connected = true;",
            "            document.getElementById('status').textContent = 'Connected';",
            "        });",
            "",
            "        document.getElementById('disconnectBtn').addEventListener('click', () => {",
            "            connected = false;",
            "            document.getElementById('status').textContent = 'Disconnected';",
            "        });",
            "",
            "        function sendCommand(peripheral, action) {",
            "            if (!connected) {",
            "                alert('Please connect first');",
            "                return;",
            "            }",
            "            console.log(`Sending command: ${peripheral}:${action}`);",
            "            // Implement actual command sending here",
            "        }",
            "    </script>",
            "</body>",
            "</html>",
            ""
        ])
        
        html_file = output_dir / "index.html"
        html_file.write_text("\n".join(html_code))
        
        return {
            'status': 'success',
            'framework': 'html',
            'files_generated': [str(html_file)],
            'output_dir': str(output_dir)
        }
