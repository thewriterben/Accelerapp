#!/bin/bash
# Accelerapp Air-Gapped Installation Script
# This script installs Accelerapp in an air-gapped environment

set -e

ACCELERAPP_VERSION="0.1.0"
INSTALL_DIR="/opt/accelerapp"
PYTHON_MIN_VERSION="3.8"

echo "====================================="
echo "Accelerapp Air-Gapped Installer"
echo "Version: ${ACCELERAPP_VERSION}"
echo "====================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Error: This script must be run as root"
    exit 1
fi

# Function to check Python version
check_python() {
    echo "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "Found Python version: ${PYTHON_VERSION}"
    
    if [ "$(echo "${PYTHON_VERSION} < ${PYTHON_MIN_VERSION}" | bc)" -eq 1 ]; then
        echo "Error: Python ${PYTHON_MIN_VERSION} or higher is required"
        exit 1
    fi
}

# Function to create directories
create_directories() {
    echo "Creating installation directories..."
    mkdir -p "${INSTALL_DIR}"/{bin,lib,models,cache,config,logs}
    mkdir -p /var/log/accelerapp
}

# Function to install Python dependencies
install_dependencies() {
    echo "Installing Python dependencies..."
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        echo "Installing pip..."
        python3 -m ensurepip --default-pip
    fi
    
    # Install from wheels directory if available (for air-gapped)
    if [ -d "wheels" ]; then
        echo "Installing from local wheels..."
        pip3 install --no-index --find-links=wheels -r requirements.txt
    else
        echo "Installing from requirements.txt..."
        pip3 install -r requirements.txt
    fi
}

# Function to install Accelerapp
install_accelerapp() {
    echo "Installing Accelerapp..."
    
    # Copy source files
    cp -r src "${INSTALL_DIR}/"
    cp setup.py "${INSTALL_DIR}/"
    cp requirements.txt "${INSTALL_DIR}/"
    cp README.md "${INSTALL_DIR}/"
    
    # Install package
    cd "${INSTALL_DIR}"
    pip3 install -e .
    
    # Create symlink for easy access
    ln -sf "${INSTALL_DIR}/bin/accelerapp" /usr/local/bin/accelerapp
}

# Function to install Ollama (if available)
install_ollama() {
    echo "Checking for Ollama installation..."
    
    if command -v ollama &> /dev/null; then
        echo "Ollama is already installed"
    else
        echo "Ollama not found. Please install manually from ollama.ai"
        echo "For air-gapped installation, copy ollama binary to /usr/local/bin/"
    fi
}

# Function to configure systemd service
configure_service() {
    echo "Configuring systemd service..."
    
    cat > /etc/systemd/system/accelerapp.service << EOF
[Unit]
Description=Accelerapp Code Generation Service
After=network.target

[Service]
Type=simple
User=accelerapp
Group=accelerapp
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/accelerapp info
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Create service user
    if ! id "accelerapp" &> /dev/null; then
        useradd -r -s /bin/false accelerapp
    fi
    
    # Set permissions
    chown -R accelerapp:accelerapp "${INSTALL_DIR}"
    chown -R accelerapp:accelerapp /var/log/accelerapp
    
    # Reload systemd
    systemctl daemon-reload
}

# Function to run health check
health_check() {
    echo "Running health check..."
    
    if command -v accelerapp &> /dev/null; then
        echo "Accelerapp installed successfully!"
        accelerapp info
    else
        echo "Error: Accelerapp installation failed"
        exit 1
    fi
}

# Main installation flow
main() {
    echo "Starting installation..."
    echo ""
    
    check_python
    create_directories
    install_dependencies
    install_accelerapp
    install_ollama
    configure_service
    health_check
    
    echo ""
    echo "====================================="
    echo "Installation Complete!"
    echo "====================================="
    echo ""
    echo "Accelerapp has been installed to: ${INSTALL_DIR}"
    echo ""
    echo "Next steps:"
    echo "1. Start the service: systemctl start accelerapp"
    echo "2. Enable on boot: systemctl enable accelerapp"
    echo "3. Check status: systemctl status accelerapp"
    echo ""
    echo "To use Accelerapp:"
    echo "  accelerapp init myproject.yaml"
    echo "  accelerapp generate myproject.yaml"
    echo ""
}

# Run main installation
main "$@"
