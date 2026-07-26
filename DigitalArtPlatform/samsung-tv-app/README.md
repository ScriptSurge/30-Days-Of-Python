# Samsung TV App (Tizen)

Smart TV application for Samsung Frame TV and other Tizen-based Samsung TVs.

## Features

- **Full-Screen Artwork Display**: Optimized for TV viewing
- **Remote Control Navigation**: D-pad and number keys
- **Slideshow Mode**: Automatic artwork rotation
- **Offline Cache**: Works without internet connection
- **Schedule Integration**: Displays artwork based on schedule rules
- **Artwork Info Overlay**: Display title, artist, and metadata
- **Settings UI**: TV-optimized settings interface
- **Pairing Flow**: Easy setup with mobile app
- **4K Support**: High-resolution artwork display
- **Low Power Mode**: Screensaver integration

## Prerequisites

- **Tizen Studio** 5.0 or higher
- **Samsung Certificate** (for physical TV testing)
- **Node.js** 18+ (for build tools)
- **TV or Emulator**: Tizen 6.0+ (2020 models and newer)

## Getting Started

### 1. Install Tizen Studio

Download from: https://developer.tizen.org/development/tizen-studio/download

Install required packages:
```bash
# Web app development
tizen-studio-install web-app-dev

# TV extensions
tizen-studio-install tv-extensions
```

### 2. Create Samsung Certificate

```bash
# Generate certificate
tizen certificate --file certificate --name "Digital Art Platform"

# Register TV device (get IP from TV settings)
sdb connect <TV_IP_ADDRESS>
```

### 3. Install Dependencies

```bash
npm install
```

### 4. Configure Environment

Edit `config/config.js`:
```javascript
export const CONFIG = {
  API_BASE_URL: 'https://api.digitalartplatform.com/api/v1',
  API_TIMEOUT: 30000,
  CACHE_SIZE_MB: 500,
  DEFAULT_INTERVAL: 3600,
};
```

### 5. Build and Run

```bash
# Build for development
npm run build

# Package for deployment
npm run package

# Install on connected TV
tizen install -n DigitalArtPlatform.wgt -t <TV_NAME>

# Run on TV
tizen run -p com.digitalartplatform.tv -t <TV_NAME>
```

## Project Structure

```
samsung-tv-app/
├── config/
│   └── config.xml         # App manifest
│
├── src/
│   ├── index.html         # Main HTML file
│   ├── main.js            # App entry point
│   │
│   ├── js/
│   │   ├── api/
│   │   │   ├── client.js           # API client
│   │   │   └── endpoints.js         # API endpoints
│   │   │
│   │   ├── services/
│   │   │   ├── artwork-service.js   # Artwork management
│   │   │   ├── cache-service.js     # Local caching
│   │   │   ├── device-service.js    # Device registration
│   │   │   └── schedule-service.js  # Schedule evaluation
│   │   │
│   │   ├── ui/
│   │   │   ├── display.js           # Artwork display
│   │   │   ├── settings.js          # Settings UI
│   │   │   ├── pairing.js           # Pairing flow
│   │   │   └── overlay.js           # Info overlay
│   │   │
│   │   ├── utils/
│   │   │   ├── storage.js           # Local storage
│   │   │   ├── network.js           # Network utilities
│   │   │   └── logger.js            # Logging
│   │   │
│   │   └── navigation.js            # Remote control handling
│   │
│   ├── css/
│   │   ├── main.css                 # Main styles
│   │   ├── display.css              # Display styles
│   │   └── settings.css             # Settings styles
│   │
│   └── assets/
│       ├── images/
│       ├── fonts/
│       └── icons/
│
├── package.json
├── .tizentide-config
└── README.md
```

## Key Features Implementation

### Device Registration

```javascript
// src/js/services/device-service.js
class DeviceService {
  async register() {
    const deviceInfo = {
      name: tizen.systeminfo.getCapability('http://tizen.org/system/model_name'),
      device_type: 'samsung_tv',
      model: tizen.systeminfo.getCapability('http://tizen.org/system/platform.name'),
      max_width: screen.width,
      max_height: screen.height,
    };
    
    const response = await api.post('/devices', deviceInfo);
    
    // Store API key
    localStorage.setItem('api_key', response.api_key);
    localStorage.setItem('device_id', response.id);
    
    return response;
  }
  
  async heartbeat() {
    const deviceId = localStorage.getItem('device_id');
    const currentArtwork = getCurrentArtwork();
    
    await api.post(`/devices/${deviceId}/heartbeat`, {
      ip_address: getIPAddress(),
      current_artwork_id: currentArtwork?.id,
    });
  }
}
```

### Artwork Display

```javascript
// src/js/ui/display.js
class ArtworkDisplay {
  constructor() {
    this.container = document.getElementById('artwork-container');
    this.image = document.getElementById('artwork-image');
    this.overlay = document.getElementById('info-overlay');
    this.currentArtwork = null;
  }
  
  async displayArtwork(artwork) {
    this.currentArtwork = artwork;
    
    // Preload image
    const img = new Image();
    img.src = artwork.high_res_url || artwork.original_url;
    
    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = reject;
    });
    
    // Fade transition
    this.image.style.opacity = 0;
    
    setTimeout(() => {
      this.image.src = img.src;
      this.image.style.opacity = 1;
      this.updateOverlay(artwork);
    }, 500);
  }
  
  updateOverlay(artwork) {
    this.overlay.innerHTML = `
      <div class="artwork-title">${artwork.title}</div>
      <div class="artwork-artist">${artwork.artist?.name || 'Unknown'}</div>
      <div class="artwork-year">${artwork.year || ''}</div>
    `;
  }
  
  showOverlay() {
    this.overlay.style.opacity = 1;
    
    // Auto-hide after 5 seconds
    setTimeout(() => this.hideOverlay(), 5000);
  }
  
  hideOverlay() {
    this.overlay.style.opacity = 0;
  }
}
```

### Remote Control Navigation

```javascript
// src/js/navigation.js
class NavigationManager {
  constructor() {
    this.setupKeyListeners();
  }
  
  setupKeyListeners() {
    document.addEventListener('keydown', (e) => {
      switch(e.keyCode) {
        case 13: // Enter
          this.handleEnter();
          break;
        case 37: // Left
          this.handleLeft();
          break;
        case 39: // Right
          this.handleRight();
          break;
        case 38: // Up
          this.handleUp();
          break;
        case 40: // Down
          this.handleDown();
          break;
        case 10009: // Return/Back
          this.handleBack();
          break;
        case 403: // Red button
          this.handleRed();
          break;
        case 404: // Green button
          this.handleGreen();
          break;
        case 405: // Yellow button
          this.handleYellow();
          break;
        case 406: // Blue button
          this.handleBlue();
          break;
      }
    });
  }
  
  handleEnter() {
    // Toggle info overlay
    display.toggleOverlay();
  }
  
  handleLeft() {
    // Previous artwork
    artworkService.previous();
  }
  
  handleRight() {
    // Next artwork
    artworkService.next();
  }
  
  handleBack() {
    // Return to previous screen or exit
    if (currentScreen === 'settings') {
      showDisplay();
    } else {
      tizen.application.getCurrentApplication().exit();
    }
  }
}
```

### Slideshow Mode

```javascript
// src/js/services/artwork-service.js
class ArtworkService {
  constructor() {
    this.interval = null;
    this.currentIndex = 0;
    this.playlist = [];
  }
  
  async startSlideshow(intervalSeconds = 3600) {
    // Fetch next artwork
    await this.loadNext();
    
    // Set interval
    this.interval = setInterval(async () => {
      await this.loadNext();
    }, intervalSeconds * 1000);
  }
  
  stopSlideshow() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
  }
  
  async loadNext() {
    try {
      const deviceId = localStorage.getItem('device_id');
      const response = await api.get(`/devices/${deviceId}/next-artwork`);
      
      await display.displayArtwork(response.artwork);
      
      // Preload next artwork
      this.preloadNext();
      
      // Update duration for next artwork
      if (response.display_duration) {
        this.updateInterval(response.display_duration);
      }
    } catch (error) {
      console.error('Failed to load next artwork:', error);
      // Fallback to cached artworks
      this.loadFromCache();
    }
  }
  
  async preloadNext() {
    // Preload next artwork for smooth transition
    const next = await api.get(`/devices/${deviceId}/next-artwork`);
    cache.preload(next.artwork.high_res_url);
  }
}
```

### Local Caching

```javascript
// src/js/services/cache-service.js
class CacheService {
  constructor(maxSizeMB = 500) {
    this.maxSize = maxSizeMB * 1024 * 1024; // Convert to bytes
    this.cacheDir = 'cache/';
  }
  
  async cache(url, data) {
    const filename = this.hashUrl(url);
    const filepath = this.cacheDir + filename;
    
    try {
      // Write file using Tizen FileSystem API
      const file = await this.openFile(filepath, 'w');
      await file.writeBytes(data);
      file.close();
      
      // Store metadata
      const metadata = {
        url: url,
        filepath: filepath,
        size: data.byteLength,
        timestamp: Date.now(),
      };
      
      this.saveMetadata(filename, metadata);
      
      // Clean up if over size limit
      await this.cleanup();
    } catch (error) {
      console.error('Failed to cache file:', error);
    }
  }
  
  async get(url) {
    const filename = this.hashUrl(url);
    const filepath = this.cacheDir + filename;
    
    try {
      const file = await this.openFile(filepath, 'r');
      const data = await file.readBytes();
      file.close();
      
      return data;
    } catch (error) {
      return null;
    }
  }
  
  async cleanup() {
    const metadata = this.getAllMetadata();
    let totalSize = metadata.reduce((sum, m) => sum + m.size, 0);
    
    if (totalSize > this.maxSize) {
      // Sort by timestamp (oldest first)
      metadata.sort((a, b) => a.timestamp - b.timestamp);
      
      // Delete oldest files until under limit
      for (const meta of metadata) {
        if (totalSize <= this.maxSize * 0.9) break; // Keep 10% buffer
        
        await this.deleteFile(meta.filepath);
        this.deleteMetadata(meta.filename);
        totalSize -= meta.size;
      }
    }
  }
}
```

### Pairing UI

```javascript
// src/js/ui/pairing.js
class PairingUI {
  async showPairingCode() {
    const code = this.generatePairingCode();
    
    // Display pairing code on screen
    document.getElementById('pairing-code').textContent = code;
    document.getElementById('pairing-screen').style.display = 'block';
    
    // Poll for pairing confirmation
    const interval = setInterval(async () => {
      const paired = await this.checkPairing(code);
      
      if (paired) {
        clearInterval(interval);
        this.onPaired(paired);
      }
    }, 2000);
    
    // Timeout after 5 minutes
    setTimeout(() => {
      clearInterval(interval);
      this.onTimeout();
    }, 300000);
  }
  
  generatePairingCode() {
    // Generate 6-digit code
    return Math.floor(100000 + Math.random() * 900000).toString();
  }
  
  async checkPairing(code) {
    try {
      const response = await api.post('/devices/check-pairing', { code });
      return response.paired ? response : null;
    } catch (error) {
      return null;
    }
  }
  
  onPaired(data) {
    localStorage.setItem('api_key', data.api_key);
    localStorage.setItem('device_id', data.device_id);
    
    // Hide pairing screen and start app
    document.getElementById('pairing-screen').style.display = 'none';
    app.start();
  }
}
```

## Testing

### On Emulator

```bash
# Launch TV emulator
tizen-emulator-manager

# Install app
tizen install -n DigitalArtPlatform.wgt -t T-samsung-6.0-x86

# Run app
tizen run -p com.digitalartplatform.tv -t T-samsung-6.0-x86
```

### On Physical TV

1. Enable Developer Mode on TV:
   - Settings → General → System Manager → Developer Mode
   - Turn on Developer Mode
   - Enter PC IP address

2. Connect to TV:
```bash
sdb connect <TV_IP_ADDRESS>
```

3. Install and run:
```bash
tizen install -n DigitalArtPlatform.wgt -t <TV_NAME>
tizen run -p com.digitalartplatform.tv -t <TV_NAME>
```

## Building for Release

### 1. Update Version

Edit `config/config.xml`:
```xml
<widget xmlns="http://www.w3.org/ns/widgets" 
        id="http://yourdomain.com/DigitalArtPlatform"
        version="1.0.0">
  <name>Digital Art Platform</name>
  ...
</widget>
```

### 2. Build Release Package

```bash
# Build optimized version
npm run build:prod

# Package
tizen package -t wgt -s <certificate-profile-name>
```

### 3. Submit to Samsung Apps TV Seller Office

1. Create account at https://seller.samsungapps.com/
2. Upload .wgt file
3. Fill in app information
4. Submit for review

## Performance Optimization

### Image Loading

```javascript
// Lazy load and progressive enhancement
async function loadImage(url) {
  // Load thumbnail first
  const thumbnail = url.replace('/high_res/', '/thumbnail/');
  await display.displayArtwork({ url: thumbnail });
  
  // Load high-res in background
  const highRes = new Image();
  highRes.src = url;
  highRes.onload = () => {
    display.displayArtwork({ url: url });
  };
}
```

### Memory Management

```javascript
// Clear unused images
function clearMemory() {
  // Force garbage collection
  if (window.gc) {
    window.gc();
  }
  
  // Clear image cache
  imageCache.clear();
}
```

## Troubleshooting

### Common Issues

**App won't install on TV**
- Ensure TV is in Developer Mode
- Check certificate validity
- Verify TV firmware version (Tizen 6.0+)

**Remote control not working**
- Check key code mappings
- Verify focus management
- Test on emulator first

**Images not loading**
- Check network connectivity
- Verify API endpoint
- Check CORS settings
- Test with cached images

**Performance issues**
- Reduce image resolution
- Increase cache size
- Optimize transitions
- Disable animations if needed

## Contributing

See [Coding Standards](../documentation/CODING_STANDARDS.md) for JavaScript code style guidelines.

## License

MIT License - see [LICENSE](../LICENSE) file for details.
