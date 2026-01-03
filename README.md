# weatherPi
# Weather Display Installation Guide

## Overview
A modern, touchscreen-optimized weather display for Raspberry Pi 5 with a 7" 1024x600 display showing current conditions and a 7-day forecast.

## Features
- 🎨 Modern dark theme with gradient accents
- 📅 7-day weather forecast
- 🌡️ Current temperature, feels-like, humidity, and wind
- 🔄 Auto-refresh every 10 minutes
- 👆 Touch-friendly interface
- 🚀 Auto-start on boot
- ⌨️ Exit fullscreen with ESC, toggle with F11

## Quick Installation

### Step 1: Download the Files
```bash
# Create a directory for the project
mkdir -p ~/weather-display
cd ~/weather-display

# Download the Python script (copy the weather_display.py content)
nano weather_display.py
# Paste the Python script content and save (Ctrl+X, Y, Enter)

# Download the setup script (copy the setup.sh content)
nano setup.sh
# Paste the setup script content and save

# Make setup script executable
chmod +x setup.sh
```

### Step 2: Get Your API Key
1. Go to [OpenWeatherMap API](https://openweathermap.org/api)
2. Click "Sign Up" and create a free account
3. Verify your email
4. Go to "API keys" in your account
5. Copy your API key (it may take a few minutes to activate)

### Step 3: Run Setup
```bash
./setup.sh
```

The setup script will:
- Install all required packages
- Configure your API key and city
- Set up autostart (optional)
- Configure screen settings (optional)

## Manual Installation

If you prefer to install manually:

### Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-tk python3-pil python3-pil.imagetk

pip3 install --break-system-packages requests pillow
```

### Configure Environment
```bash
cd ~/weather-display

# Create config file
cat > .env << EOF
export WEATHER_API_KEY="your_api_key_here"
export WEATHER_CITY="your_city_name"
EOF

# Create start script
cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .env
python3 weather_display.py
EOF

chmod +x start.sh
```

### Run the Display
```bash
./start.sh
```

## Configuration

### Change City or API Key
```bash
nano ~/weather-display/.env
```

Edit the values:
```bash
export WEATHER_API_KEY="your_new_key"
export WEATHER_CITY="New York"
```

### Change Units
Edit `weather_display.py` and change:
```python
self.UNITS = 'imperial'  # For Fahrenheit
# or
self.UNITS = 'metric'    # For Celsius
```

## Autostart Configuration

### Using systemd (Recommended)
The setup script creates this for you, but here's the manual method:

```bash
sudo nano /etc/systemd/system/weather-display.service
```

Paste:
```ini
[Unit]
Description=Weather Display
After=graphical.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
ExecStartPre=/bin/sleep 10
ExecStart=/home/pi/weather-display/start.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=graphical.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-display.service
sudo systemctl start weather-display.service
```

### Check Status
```bash
# Check if running
sudo systemctl status weather-display.service

# View live logs
journalctl -u weather-display.service -f

# Restart service
sudo systemctl restart weather-display.service

# Stop service
sudo systemctl stop weather-display.service
```

## Screen Configuration

### Disable Screen Blanking
```bash
# Edit autostart file
nano ~/.config/lxsession/LXDE-pi/autostart
```

Add these lines:
```bash
@xset s off
@xset -dpms
@xset s noblank
```

### Rotate Display (if needed)
Edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add:
```bash
# Rotate 90 degrees
display_rotate=1

# Rotate 180 degrees
display_rotate=2

# Rotate 270 degrees
display_rotate=3
```

Reboot after changes:
```bash
sudo reboot
```

## Troubleshooting

### Display Doesn't Start
```bash
# Check if service is running
sudo systemctl status weather-display.service

# View error logs
journalctl -u weather-display.service -n 50

# Test manually
cd ~/weather-display
source .env
python3 weather_display.py
```

### API Errors
- Verify your API key is correct
- Wait 10-15 minutes after creating new API key (activation time)
- Check internet connection: `ping openweathermap.org`
- Verify city name is spelled correctly

### Display Issues
```bash
# Check DISPLAY variable
echo $DISPLAY  # Should show :0

# Check X authority
ls -la ~/.Xauthority

# Test if GUI works
python3 -c "import tkinter; tkinter.Tk()"
```

### Screen Too Small/Large
The display is optimized for 1024x600. For different resolutions, edit font sizes in `weather_display.py`.

## Customization

### Change Theme Colors
Edit these values in `weather_display.py`:
```python
# Background colors
'#0a0e27'  # Main background (dark blue)
'#1a1f3a'  # Card background (lighter blue)

# Text colors
'#ffffff'  # White text
'#8892b0'  # Gray text
'#64ffda'  # Accent color (teal)
```

### Add More Days
Change the forecast loop (note: API free tier provides 5 days):
```python
for i in range(5):  # Change from 7 to 5 if needed
```

### Update Frequency
Change auto-refresh interval (in milliseconds):
```python
self.root.after(600000, self.update_weather)  # 600000 = 10 minutes
```

## Uninstall

```bash
# Stop and disable service
sudo systemctl stop weather-display.service
sudo systemctl disable weather-display.service
sudo rm /etc/systemd/system/weather-display.service
sudo systemctl daemon-reload

# Remove files
rm -rf ~/weather-display

# Remove screen blanking config (if added)
nano ~/.config/lxsession/LXDE-pi/autostart
# Remove the xset lines
```

## Credits
- Weather data from [OpenWeatherMap](https://openweathermap.org)
- Designed for Raspberry Pi OS with Desktop

## Support
For issues or questions:
- Check OpenWeatherMap API status
- Verify Raspberry Pi OS is up to date: `sudo apt-get update && sudo apt-get upgrade`
- Ensure display drivers are properly installed
