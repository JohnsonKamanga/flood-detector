# Getting Started with Urban Flood Prediction System

This guide will help you set up and run the Urban Flood Prediction System on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

- **Docker Desktop** (v20.10 or higher)
  - [Download for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Download for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - [Download for Linux](https://docs.docker.com/desktop/install/linux-install/)
- **Docker Compose** (usually included with Docker Desktop)
- **Git** for cloning the repository

### Optional (for development)

- **Python 3.11+** (for local backend development)
- **Node.js 18+** (for local frontend development)
- **PostgreSQL 15+** with PostGIS (if running database locally)

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd flood-detector
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:your_password@db:5432/flood_prediction

# Or use Supabase (recommended for production)
# DATABASE_URL=postgresql+asyncpg://postgres.xxx:password@aws-0-region.pooler.supabase.com:5432/postgres

# Application Settings
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000","http://localhost"]

# Frontend Environment Variables
VITE_API_BASE_URL=/api
VITE_WS_URL=ws://localhost/ws

# Server Ports
PORT=80
BACKEND_PORT=8000
```

### Step 3: Start the Application

Using Docker Compose (recommended):

```bash
# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up --build -d
```

This will start:

- **PostgreSQL database** with PostGIS on port 5432
- **Backend API** on port 8000
- **Frontend** on port 80 (<http://localhost>)

### Step 4: Seed Initial Data

Populate the database with river gauge locations:

```bash
# Seed gauge data
docker compose exec backend python3 scripts/seed_gauges.py
```

This adds 25+ river gauges from high-risk flood zones worldwide.

### Step 5: Access the Application

Open your browser and navigate to:

- **Frontend**: <http://localhost>
- **API Documentation**: <http://localhost:8000/docs>
- **API Redoc**: <http://localhost:8000/redoc>

## 🗄️ Database Setup

### Using Local PostgreSQL

If using the included PostgreSQL container, the database is automatically initialized.

### Using Supabase (Production)

1. Create a Supabase project at <https://supabase.com>
2. Get your connection string from Project Settings → Database
3. Update `DATABASE_URL` in `.env`:

   ```env
   DATABASE_URL=postgresql+asyncpg://postgres.xxx:password@aws-0-region.pooler.supabase.com:5432/postgres
   ```

4. Enable PostGIS extension in Supabase:
   - Go to Database → Extensions
   - Enable "postgis"

### Database Migrations

The application automatically creates tables on startup. To manually run migrations:

```bash
# Access backend container
docker compose exec backend bash

# Run migrations (if using Alembic)
alembic upgrade head
```

## 🔧 Configuration Details

### Backend Configuration

The backend is configured via environment variables and `backend/app/config.py`:

#### Key Settings

- `DATABASE_URL`: Database connection string
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `CORS_ORIGINS`: Allowed origins for CORS
- `DATA_REFRESH_INTERVAL`: How often to refresh gauge data (seconds)

### Frontend Configuration

The frontend uses runtime configuration via `config.js`:

#### Environment Variables

- `VITE_API_BASE_URL`: Backend API endpoint (default: `/api`)
- `VITE_WS_URL`: WebSocket endpoint (default: auto-detected)

These are injected at container startup, allowing the same build to work in different environments.

### Background Tasks

The system runs several automated tasks:

| Task | Interval | Description |
|------|----------|-------------|
| Gauge Data Ingestion | 5 minutes | Fetch latest river gauge readings |
| Weather Data Ingestion | 15 minutes | Update weather forecasts |
| Flood Predictions | 10 minutes | Calculate flood risk assessments |
| Data Cleanup | Daily at 2 AM | Remove old measurements |

Configure intervals in `backend/app/tasks/scheduled_tasks.py`.

## 🧪 Verification

### Check Service Health

```bash
# Check all services are running
docker compose ps

# View logs
docker compose logs -f

# Check backend health
curl http://localhost:8000/health

# Check database connection
docker compose exec backend python3 -c "from app.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### Test API Endpoints

```bash
# Get all gauges
curl http://localhost:8000/api/gauges/

# Get flood predictions
curl http://localhost:8000/api/predictions/

# Get historical flood statistics
curl http://localhost:8000/api/historical/statistics
```

### Test WebSocket Connection

Open browser console on <http://localhost> and run:

```javascript
const ws = new WebSocket('ws://localhost/ws/flood-updates');
ws.onmessage = (event) => console.log('Received:', JSON.parse(event.data));
ws.onopen = () => ws.send(JSON.stringify({type: 'subscribe', resource: 'predictions'}));
```

## 🛠️ Development Setup

### Backend Development

For local backend development without Docker:

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

For local frontend development:

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Access at <http://localhost:5173>

### Database Access

```bash
# Connect to PostgreSQL
docker compose exec db psql -U postgres -d flood_prediction

# Common queries
\dt                          # List tables
SELECT COUNT(*) FROM river_gauges;
SELECT * FROM river_gauges LIMIT 5;
```

## 📊 Adding Custom Data

### Add New River Gauges

Edit `backend/scripts/seed_gauges.py`:

```python
MANUAL_GAUGES = [
    {
        "usgs_site_id": "MANUAL_XX_01",
        "name": "Your River at Your City",
        "latitude": 0.0,
        "longitude": 0.0
    },
    # ... more gauges
]
```

Then run:

```bash
docker compose exec backend python3 scripts/seed_gauges.py
```

### Add Historical Flood Events

Use the API or admin interface:

```bash
curl -X POST http://localhost:8000/api/historical/ \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "2024 Spring Flood",
    "event_date": "2024-03-15T12:00:00Z",
    "location_name": "City Name",
    "severity": "major",
    "peak_gauge_height_ft": 25.5,
    "estimated_damage_usd": 5000000,
    "description": "Heavy rainfall caused major flooding"
  }'
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using port 80
sudo lsof -i :80

# Change port in docker-compose.yaml
ports:
  - "8080:80"  # Use port 8080 instead
```

#### 2. Database Connection Failed

```bash
# Check database is running
docker compose ps db

# View database logs
docker compose logs db

# Restart database
docker compose restart db
```

#### 3. Frontend Can't Connect to Backend

- Check `VITE_API_BASE_URL` in `.env`
- Verify nginx proxy configuration in `frontend/nginx.conf.template`
- Check browser console for CORS errors

#### 4. Background Tasks Not Running

```bash
# Check scheduler logs
docker compose logs backend | grep "Scheduler"

# Verify APScheduler is installed
docker compose exec backend pip list | grep APScheduler
```

#### 5. HTTPS Redirect Issues (Production)

- Ensure `--proxy-headers` flag is set in uvicorn command
- Check `X-Forwarded-Proto` headers are being sent by your proxy

### Reset Everything

```bash
# Stop and remove all containers
docker compose down

# Remove volumes (WARNING: deletes all data)
docker compose down -v

# Rebuild from scratch
docker compose up --build
```

## 📚 Next Steps

- Read the [API Documentation](http://localhost:8000/docs)
- Explore the [Frontend Components](./frontend/src/components)
- Review [Backend Services](./backend/app/services)
- Check out the [Roadmap](./README.md#-roadmap)

## 🆘 Getting Help

- **Documentation**: Check README.md and code comments
- **API Docs**: <http://localhost:8000/docs>
- **Issues**: Open an issue on GitHub
- **Logs**: `docker compose logs -f` for real-time logs

## 🎯 Quick Commands Reference

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f [service_name]

# Restart a service
docker compose restart [service_name]

# Execute command in container
docker compose exec [service_name] [command]

# Rebuild specific service
docker compose up --build [service_name]

# Seed database
docker compose exec backend python3 scripts/seed_gauges.py

# Access database
docker compose exec db psql -U postgres -d flood_prediction

# Run backend shell
docker compose exec backend bash

# Run frontend shell
docker compose exec frontend sh
```

---

Ready to predict floods? Let's go! 🌊
