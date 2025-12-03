# Urban Flood Prediction System

A real-time flood prediction and monitoring system that provides early warnings and risk assessments for urban areas worldwide. The system integrates data from river gauges, weather forecasts, and historical flood events to predict and visualize flood risks.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.x-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

## 🌊 Features

### Real-Time Monitoring

- **Live River Gauge Data**: Monitors 25+ river gauges across high-risk flood zones worldwide
- **Weather Integration**: Fetches real-time weather forecasts from NOAA/NWS
- **WebSocket Updates**: Real-time data streaming to connected clients
- **Interactive Map**: Visualize gauges, flood zones, and risk areas on an interactive map

### Flood Prediction

- **Risk Assessment**: Multi-factor risk calculation based on:
  - River gauge heights and flow rates
  - Rainfall forecasts
  - Soil saturation levels
  - Proximity to water bodies
- **Spatial Analysis**: Geographic risk zone generation using interpolation
- **Confidence Scoring**: Prediction confidence based on data freshness and availability

### Historical Data

- **Flood Event Database**: Track and analyze past flood events
- **Impact Assessment**: Record casualties, evacuations, and economic damage
- **Statistical Analysis**: Trends, recurrence intervals, and return periods
- **Verification System**: Verified vs. unverified flood event tracking

### Automated Background Tasks

- **Data Ingestion**: Automatic gauge and weather data updates every 5-15 minutes
- **Flood Predictions**: Automated risk calculations every 10 minutes
- **Data Cleanup**: Scheduled cleanup of old measurements

## 🏗️ Architecture

### Backend (FastAPI + Python)

- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with PostGIS for geospatial data
- **Task Scheduler**: APScheduler for background jobs
- **External APIs**:
  - USGS Water Services API
  - NOAA/NWS Weather API
- **Key Services**:
  - Data ingestion (USGS, Weather)
  - Flood prediction and risk calculation
  - Historical flood management
  - WebSocket real-time updates

### Frontend (React + TypeScript)

- **Framework**: React 18 with TypeScript
- **Routing**: React Router v6
- **Styling**: Tailwind CSS
- **Maps**: Leaflet for interactive mapping
- **State Management**: React hooks
- **Real-time**: WebSocket client for live updates

### Infrastructure

- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (frontend reverse proxy)
- **Database**: PostgreSQL 15 with PostGIS extension
- **Deployment**: Railway-ready with production configurations

## 🌍 Coverage

The system monitors flood-prone areas across:

- **Asia**: Bangladesh, India, Pakistan, Sri Lanka, Thailand, Vietnam
- **Africa**: Egypt, Malawi, Mozambique, Nigeria
- **South America**: Argentina, Brazil, Colombia
- **Europe**: Germany, Italy, United Kingdom
- **North America**: United States (Texas, Louisiana, Florida)
- **Australia/Oceania**: Australia

## 📊 Data Sources

- **USGS Water Services**: Real-time river gauge data
- **NOAA/NWS**: Weather forecasts and precipitation data
- **Manual Gauges**: Custom monitoring points for international locations
- **Historical Records**: User-contributed and verified flood event data

## 🚀 Quick Start

See [GETTING_STARTED.md](./GETTING_STARTED.md) for detailed setup instructions.

```bash
# Clone the repository
git clone <repository-url>
cd flood-detector

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Start the application
docker compose up --build

# Seed initial gauge data
docker compose exec backend python3 scripts/seed_gauges.py
```

Access the application at `http://localhost:3000`

## 📁 Project Structure

```
flood-detector/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── spatial/        # Geospatial processing
│   │   ├── tasks/          # Background tasks
│   │   └── utils/          # Utilities
│   ├── scripts/            # Database seeding scripts
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API & WebSocket clients
│   │   └── types/          # TypeScript types
│   └── package.json        # Node dependencies
├── docker-compose.yaml     # Docker orchestration
└── .env                    # Environment configuration
```

## 🔧 Configuration

### Environment Variables

#### Backend

- `DATABASE_URL`: PostgreSQL connection string
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `CORS_ORIGINS`: Allowed CORS origins

#### Frontend

- `VITE_API_BASE_URL`: Backend API URL
- `VITE_WS_URL`: WebSocket server URL

See `.env.example` for complete configuration options.

## 📡 API Endpoints

### Gauges

- `GET /api/gauges/` - List all active gauges
- `GET /api/gauges/{id}` - Get specific gauge details
- `GET /api/gauges/{id}/measurements` - Get gauge measurements
- `POST /api/gauges/refresh/{site_id}` - Refresh gauge data

### Predictions

- `GET /api/predictions/` - List flood predictions
- `GET /api/predictions/latest` - Get latest prediction
- `POST /api/predictions/calculate` - Calculate risk for location
- `GET /api/predictions/zones` - Get risk zones
- `GET /api/predictions/heatmap` - Get risk heatmap

### Historical

- `GET /api/historical/` - List historical floods
- `GET /api/historical/{id}` - Get flood details
- `GET /api/historical/statistics` - Get flood statistics
- `GET /api/historical/location/nearby` - Find nearby floods
- `POST /api/historical/` - Create flood record

### WebSocket

- `WS /ws/flood-updates` - Real-time flood updates

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Adding New Gauges

Edit `backend/scripts/seed_gauges.py` and add to `MANUAL_GAUGES` list:

```python
{
    "usgs_site_id": "MANUAL_XX_01",
    "name": "River Name at City, Country",
    "latitude": 0.0,
    "longitude": 0.0
}
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **USGS**: United States Geological Survey for river gauge data
- **NOAA/NWS**: National Weather Service for weather forecasts
- **OpenStreetMap**: Map data and tiles
- **PostGIS**: Geospatial database extension

## 📞 Support

For issues, questions, or contributions:

- Open an issue on GitHub
- Contact: [johnsonkamanga2@gmail.com]

## 🗺️ Roadmap

- [ ] Machine learning-based flood prediction models
- [ ] Mobile application (iOS/Android)
- [ ] SMS/Email alert notifications
- [ ] Integration with additional weather APIs
- [ ] Community reporting features
- [ ] Multi-language support
- [ ] Advanced visualization (3D flood modeling)

---

Built with ❤️ for safer communities worldwide
