#!/bin/bash
# Setup script for Weather Display on Raspberry Pi
# Run with: bash setup.sh

set -e

echo "================================================"
echo "Weather Display Setup for Raspberry Pi"
echo "================================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Updating system packages..."
sudo apt-get update

# Install required packages
echo "Installing required packages..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-tk \
    python3-pil \
    python3-pil.imagetk \
    git

# Install Python packages
echo "Installing Python packages..."
pip3 install --break-system-packages requests pillow || pip3 install requests pillow

# Create project directory
INSTALL_DIR="$HOME/weather-display"
echo "Creating project directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

# Save the weather script
cat > "$INSTALL_DIR/weather_display.py" << 'EOFPYTHON'
# The Python script will be created separately
EOFPYTHON

echo ""
echo "================================================"
echo "API Key Configuration"
echo "================================================"
echo ""
echo "You need a free API key from OpenWeatherMap:"
echo "1. Go to https://openweathermap.org/api"
echo "2. Sign up for a free account"
echo "3. Get your API key from the API keys section"
echo ""

read -p "Enter your OpenWeatherMap API key: " API_KEY
read -p "Enter your city name (e.g., London, New York): " CITY

# Create config file
cat > "$INSTALL_DIR/.env" << EOF
export WEATHER_API_KEY="$API_KEY"
export WEATHER_CITY="$CITY"
EOF

# Create startup script
cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .env
python3 weather_display.py
EOF

chmod +x "$INSTALL_DIR/start.sh"

# Create systemd service for autostart
echo ""
read -p "Configure autostart on boot? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo tee /etc/systemd/system/weather-display.service > /dev/null << EOF
[Unit]
Description=Weather Display
After=graphical.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$USER/.Xauthority
ExecStartPre=/bin/sleep 10
ExecStart=$INSTALL_DIR/start.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=graphical.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable weather-display.service
    echo "✓ Autostart configured"
fi

# Configure screen settings
echo ""
read -p "Configure screen settings (disable screensaver, etc)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Disable screen blanking
    cat >> "$HOME/.config/lxsession/LXDE-pi/autostart" << EOF

# Weather Display settings
@xset s off
@xset -dpms
@xset s noblank
EOF
    echo "✓ Screen settings configured"
fi

echo ""
echo "================================================"
echo "Installation Complete!"
echo "================================================"
echo ""
echo "Installation directory: $INSTALL_DIR"
echo ""
echo "To start the weather display manually:"
echo "  cd $INSTALL_DIR && ./start.sh"
echo ""
echo "To start the service:"
echo "  sudo systemctl start weather-display.service"
echo ""
echo "To check service status:"
echo "  sudo systemctl status weather-display.service"
echo ""
echo "To view logs:"
echo "  journalctl -u weather-display.service -f"
echo ""
echo "The display will start automatically on next boot."
echo ""
read -p "Would you like to start the weather display now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$INSTALL_DIR" && ./start.sh
fi
