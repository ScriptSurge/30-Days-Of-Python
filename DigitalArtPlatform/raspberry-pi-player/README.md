# Raspberry Pi Player

Display client for Raspberry Pi to show artwork on any HDMI display.

## Features

- **4K Support**: Display artwork at up to 4K resolution
- **Auto-Start**: Launches automatically on boot
- **Fullscreen Kiosk**: Dedicated display mode
- **Offline Cache**: Works without internet
- **Remote Control**: Managed via API or web interface
- **Low Power**: Optimized for 24/7 operation
- **Hardware Acceleration**: GPU-accelerated rendering
- **Multiple Display Modes**: Fit, fill, stretch options
- **Web Configuration**: Browser-based setup

## Requirements

- **Raspberry Pi**: Pi 3B+ or newer (Pi 4 recommended for 4K)
- **OS**: Raspberry Pi OS (64-bit recommended)
- **RAM**: 2GB minimum, 4GB+ recommended
- **Storage**: 16GB SD card minimum
- **Display**: HDMI monitor or TV

## Quick Start

### 1. Flash SD Card

Download Raspberry Pi Imager: https://www.raspberrypi.com/software/

Flash Raspberry Pi OS (64-bit) to SD card.

### 2. Initial Setup

Boot Raspberry Pi and complete initial setup:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv git chromium-browser unclutter
```

### 3. Install Application

```bash
# Clone repository
git clone https://github.com/yourusername/digital-art-platform.git
cd digital-art-platform/raspberry-pi-player

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy configuration
cp config.example.json config.json
# Edit config.json with your settings
```

### 4. Configure Auto-Start

```bash
# Install as systemd service
sudo cp digitalart-player.service /etc/systemd/system/
sudo systemctl enable digitalart-player
sudo systemctl start digitalart-player

# Check status
sudo systemctl status digitalart-player
```

### 5. Access Web Configuration

Open browser and navigate to:
```
http://<raspberry-pi-ip>:8080
```

## Project Structure

```
raspberry-pi-player/
├── src/
│   ├── main.py              # Application entry point
│   ├── player.py            # Display player
│   ├── api_client.py        # API communication
│   ├── cache.py             # Local caching
│   ├── config.py            # Configuration management
│   ├── display.py           # Display management
│   └── web_server.py        # Web configuration interface
│
├── web/
│   ├── index.html           # Configuration UI
│   ├── app.js
│   └── styles.css
│
├── scripts/
│   ├── install.sh           # Installation script
│   ├── update.sh            # Update script
│   └── uninstall.sh         # Uninstallation script
│
├── config.example.json
├── requirements.txt
├── digitalart-player.service
└── README.md
```

## Implementation Approaches

### Approach 1: Python + Pygame (Recommended)

Lightweight Python-based player with hardware acceleration.

**Benefits:**
- Low resource usage
- Direct hardware acceleration
- Simple to maintain
- Good for 24/7 operation

**Installation:**
```bash
pip install pygame pillow requests
```

**Code:**
```python
# src/player.py
import pygame
import requests
from PIL import Image
from io import BytesIO

class ArtworkPlayer:
    def __init__(self, config):
        pygame.init()
        
        # Get display info
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        
        # Create fullscreen window
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        
        pygame.display.set_caption('Digital Art Player')
        pygame.mouse.set_visible(False)
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def display_artwork(self, artwork_url):
        try:
            # Download image
            response = requests.get(artwork_url)
            img = Image.open(BytesIO(response.content))
            
            # Resize to fit screen
            img = self.resize_image(img, self.width, self.height)
            
            # Convert to pygame surface
            img_str = img.tobytes()
            surface = pygame.image.fromstring(img_str, img.size, img.mode)
            
            # Display
            self.screen.fill((0, 0, 0))
            
            # Center image
            x = (self.width - surface.get_width()) // 2
            y = (self.height - surface.get_height()) // 2
            
            self.screen.blit(surface, (x, y))
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error displaying artwork: {e}")
    
    def resize_image(self, img, max_width, max_height):
        # Calculate aspect ratio
        aspect = img.width / img.height
        target_aspect = max_width / max_height
        
        if aspect > target_aspect:
            # Image is wider
            new_width = max_width
            new_height = int(max_width / aspect)
        else:
            # Image is taller
            new_height = max_height
            new_width = int(max_height * aspect)
        
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.clock.tick(60)
        
        pygame.quit()
```

### Approach 2: Electron Kiosk

Full web browser in kiosk mode.

**Benefits:**
- Rich UI capabilities
- Web technologies (HTML/CSS/JS)
- Easy to update
- Same codebase as web dashboard

**Installation:**
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Electron
npm install electron
```

**Kiosk script:**
```bash
#!/bin/bash
# start-kiosk.sh

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Hide cursor
unclutter -idle 0.5 -root &

# Start Chromium in kiosk mode
chromium-browser \
  --kiosk \
  --noerrdialogs \
  --disable-infobars \
  --no-first-run \
  --app=http://localhost:8080
```

## Configuration

### config.json

```json
{
  "api": {
    "base_url": "https://api.digitalartplatform.com/api/v1",
    "api_key": "your-device-api-key",
    "device_id": 123
  },
  "display": {
    "mode": "fit",
    "background_color": "#000000",
    "transition_duration": 1000,
    "show_info_overlay": true,
    "overlay_duration": 5000
  },
  "slideshow": {
    "interval": 3600,
    "shuffle": false,
    "preload_next": true
  },
  "cache": {
    "enabled": true,
    "max_size_mb": 2000,
    "directory": "/var/cache/digitalart"
  },
  "system": {
    "auto_update": true,
    "log_level": "INFO",
    "gpu_acceleration": true
  }
}
```

## Main Application

```python
# src/main.py
import asyncio
import signal
from player import ArtworkPlayer
from api_client import APIClient
from cache import CacheManager
from config import load_config
from web_server import WebServer

class Application:
    def __init__(self):
        self.config = load_config()
        self.player = ArtworkPlayer(self.config)
        self.api_client = APIClient(self.config)
        self.cache = CacheManager(self.config)
        self.web_server = WebServer(self.config, self)
        self.running = True
    
    async def start(self):
        # Start web server for configuration
        await self.web_server.start()
        
        # Register device if not already registered
        if not self.config.get('api', {}).get('device_id'):
            await self.register_device()
        
        # Start slideshow
        await self.run_slideshow()
    
    async def register_device(self):
        device_info = {
            'name': 'Raspberry Pi Player',
            'device_type': 'raspberry_pi',
            'model': get_pi_model(),
            'max_width': 3840,
            'max_height': 2160,
        }
        
        device = await self.api_client.register_device(device_info)
        
        self.config['api']['device_id'] = device['id']
        self.config['api']['api_key'] = device['api_key']
        save_config(self.config)
    
    async def run_slideshow(self):
        while self.running:
            try:
                # Get next artwork
                artwork = await self.api_client.get_next_artwork()
                
                # Check cache first
                cached_path = self.cache.get(artwork['high_res_url'])
                
                if cached_path:
                    self.player.display_artwork_from_file(cached_path)
                else:
                    # Download and cache
                    image_data = await self.api_client.download_image(
                        artwork['high_res_url']
                    )
                    cached_path = self.cache.save(
                        artwork['high_res_url'],
                        image_data
                    )
                    self.player.display_artwork_from_file(cached_path)
                
                # Send heartbeat
                await self.api_client.heartbeat(artwork['id'])
                
                # Wait for interval
                interval = self.config['slideshow']['interval']
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"Error in slideshow loop: {e}")
                await asyncio.sleep(60)
    
    def stop(self):
        self.running = False
        self.player.cleanup()

def main():
    app = Application()
    
    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        print("Shutting down...")
        app.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run application
    asyncio.run(app.start())

if __name__ == '__main__':
    main()
```

## Web Configuration Interface

```python
# src/web_server.py
from aiohttp import web
import json

class WebServer:
    def __init__(self, config, app):
        self.config = config
        self.app = app
        self.web_app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        self.web_app.router.add_get('/', self.index)
        self.web_app.router.add_get('/api/config', self.get_config)
        self.web_app.router.add_post('/api/config', self.update_config)
        self.web_app.router.add_post('/api/pair', self.pair_device)
        self.web_app.router.add_get('/api/status', self.get_status)
    
    async def index(self, request):
        with open('web/index.html') as f:
            return web.Response(text=f.read(), content_type='text/html')
    
    async def get_config(self, request):
        return web.json_response(self.config)
    
    async def update_config(self, request):
        data = await request.json()
        self.config.update(data)
        save_config(self.config)
        return web.json_response({'success': True})
    
    async def get_status(self, request):
        return web.json_response({
            'online': True,
            'current_artwork': self.app.player.current_artwork,
            'cache_size': self.app.cache.get_size(),
            'uptime': get_uptime(),
        })
    
    async def start(self):
        runner = web.AppRunner(self.web_app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
```

## Hardware Optimization

### GPU Acceleration

Enable GPU acceleration in `/boot/config.txt`:
```ini
# Enable GPU memory
gpu_mem=256

# Enable hardware acceleration
dtoverlay=vc4-kms-v3d
max_framebuffers=2
```

### Overclocking (Pi 4)

```ini
# /boot/config.txt
over_voltage=6
arm_freq=2000
gpu_freq=750
```

### Cooling

Recommended for 24/7 operation:
- Active cooling (fan)
- Heatsinks on CPU and RAM
- Good ventilation

## Monitoring

### System Monitoring

```python
import psutil

def get_system_stats():
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'temperature': get_cpu_temperature(),
        'disk_usage': psutil.disk_usage('/').percent,
    }

def get_cpu_temperature():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp') as f:
            temp = float(f.read()) / 1000.0
            return temp
    except:
        return None
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/digitalart-player.log'),
        logging.StreamHandler()
    ]
)
```

## Troubleshooting

### Display Issues

**Black screen:**
```bash
# Check HDMI output
tvservice -s

# Force HDMI mode
# Edit /boot/config.txt
hdmi_force_hotplug=1
hdmi_drive=2
```

**Wrong resolution:**
```bash
# List supported modes
tvservice -m CEA
tvservice -m DMT

# Set specific mode in /boot/config.txt
hdmi_group=1
hdmi_mode=16  # 1080p 60Hz
```

### Performance Issues

```bash
# Check temperature
vcgencmd measure_temp

# Check throttling
vcgencmd get_throttled

# Increase GPU memory
sudo nano /boot/config.txt
# Set gpu_mem=256 or higher
```

### Network Issues

```bash
# Check connectivity
ping -c 4 api.digitalartplatform.com

# Test API
curl https://api.digitalartplatform.com/api/v1/health
```

## Updates

### Manual Update

```bash
cd /home/pi/digital-art-platform/raspberry-pi-player
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart digitalart-player
```

### Auto-Update Script

```bash
#!/bin/bash
# scripts/auto-update.sh

cd /home/pi/digital-art-platform/raspberry-pi-player
git fetch

if [ $(git rev-list HEAD...origin/main --count) != 0 ]; then
    git pull
    source venv/bin/activate
    pip install -r requirements.txt
    sudo systemctl restart digitalart-player
    echo "Updated to latest version"
fi
```

Add to crontab:
```bash
crontab -e
# Add line:
0 3 * * * /home/pi/digital-art-platform/raspberry-pi-player/scripts/auto-update.sh
```

## Security

### Firewall

```bash
# Install UFW
sudo apt install ufw

# Allow SSH and web interface
sudo ufw allow 22
sudo ufw allow 8080

# Enable firewall
sudo ufw enable
```

### Auto-Updates

```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## Contributing

See [Coding Standards](../documentation/CODING_STANDARDS.md) for Python code style guidelines.

## License

MIT License - see [LICENSE](../LICENSE) file for details.
