# Digital Art Platform

> An open-source digital art platform for Samsung Frame TV and smart displays

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## 🎨 Vision

Replace the Samsung Art Store with a complete open-source solution that combines the best features of:

- **Samsung Art Store** - Beautiful artwork display
- **Apple Photos** - Intuitive photo management
- **Plex** - Self-hosted media server
- **Spotify** - Curated collections and playlists
- **Google Photos** - Smart organization
- **Digital Museum Exhibits** - Curated art experiences

## ✨ Features

### Core Features
- 🖼️ Display artwork, photography, AI-generated art, and personal photos
- 📱 iOS app for browsing and control
- 🖥️ Web dashboard for management
- 📺 Samsung Frame TV app (Tizen)
- 🔌 Raspberry Pi player for any display
- ☁️ Multiple cloud storage integrations
- 🎨 AI-powered features and recommendations
- 📅 Smart scheduling by time, season, and events
- 💾 Offline caching
- 🔐 Secure authentication and authorization

### Artwork Sources
- **Public Domain Museums**: Met Museum, Art Institute of Chicago, Rijksmuseum, National Gallery, Europeana
- **Stock Photography**: NASA, Unsplash, Pexels
- **User Uploads**: Local files, Google Drive, Dropbox, OneDrive, NAS/SMB shares
- **AI Art**: OpenAI DALL-E, Stable Diffusion, Flux

### Smart Features
- 🎯 Curated collections
- ❤️ Favorites and playlists
- 🔀 Infinite shuffle mode
- 📅 Schedule artwork by time of day, season, or holidays
- 🤖 AI-powered recommendations
- 🎨 Color palette extraction
- 🔍 Advanced search (artist, museum, year, style, color, keywords)
- 📊 Viewing analytics

## 🏗️ Architecture

This is a monorepo containing all platform components:

```
DigitalArtPlatform/
├── backend/              # FastAPI backend (Python)
├── ios-app/             # SwiftUI iOS app
├── web-dashboard/       # React + TypeScript admin dashboard
├── samsung-tv-app/      # Tizen TV app (JavaScript)
├── raspberry-pi-player/ # Python/Electron display client
├── shared/              # Shared models, types, and utilities
└── documentation/       # Architecture docs, diagrams, API specs
```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL |
| **iOS App** | Swift 5.9+, SwiftUI, MVVM |
| **Web Dashboard** | React 18+, TypeScript, Tailwind CSS, Vite |
| **TV App** | Tizen Web API, JavaScript ES6+ |
| **Pi Player** | Python 3.11+, Electron/Kiosk |
| **Infrastructure** | Docker, Docker Compose, GitHub Actions |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL 15+ (or use Docker)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/digital-art-platform.git
cd digital-art-platform

# Start backend with Docker
cd backend
docker-compose up -d

# Or run locally
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Start web dashboard
cd ../web-dashboard
npm install
npm run dev

# The API will be available at http://localhost:8000
# The web dashboard at http://localhost:5173
# API docs at http://localhost:8000/docs
```

## 📖 Documentation

- [System Architecture](./documentation/ARCHITECTURE.md)
- [Database Schema](./documentation/DATABASE_SCHEMA.md)
- [API Specification](./documentation/API_SPECIFICATION.md)
- [Development Roadmap](./documentation/ROADMAP.md)
- [Coding Standards](./documentation/CODING_STANDARDS.md)
- [Deployment Guide](./documentation/DEPLOYMENT.md)
- [Contributing Guide](./documentation/CONTRIBUTING.md)

## 🎯 Development Roadmap

### Phase 1: Foundation (Weeks 1-4)
- ✅ Project architecture and documentation
- ⏳ Backend core (FastAPI, PostgreSQL, authentication)
- ⏳ Database schema implementation
- ⏳ Basic REST API
- ⏳ Docker setup

### Phase 2: Core Features (Weeks 5-8)
- ⏳ Image processing and caching
- ⏳ Public domain museum integrations
- ⏳ Web dashboard MVP
- ⏳ User management
- ⏳ Collection and playlist features

### Phase 3: Client Apps (Weeks 9-12)
- ⏳ iOS app development
- ⏳ Raspberry Pi player
- ⏳ Samsung TV app (Tizen)
- ⏳ Offline caching

### Phase 4: Intelligence (Weeks 13-16)
- ⏳ AI features (description generation, recommendations)
- ⏳ Scheduling system
- ⏳ Search optimization
- ⏳ Analytics

### Phase 5: Polish & Scale (Weeks 17-20)
- ⏳ Performance optimization
- ⏳ Additional integrations (cloud storage, AI art)
- ⏳ Advanced features
- ⏳ Production deployment

### Phase 6: Future (Beyond Week 20)
- ⏳ Apple Vision Pro support
- ⏳ Home Assistant integration
- ⏳ Apple TV app
- ⏳ Voice control
- ⏳ Multi-user SaaS features

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./documentation/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Museum APIs for providing free access to public domain artwork
- Open source community for the amazing tools and libraries
- Samsung Frame TV for the inspiration

## 📞 Support

- 📧 Email: support@digitalartplatform.com
- 💬 Discord: [Join our community](#)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/digital-art-platform/issues)

---

**Built with ❤️ for art lovers and technologists**
