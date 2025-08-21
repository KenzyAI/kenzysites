# Bolt.DIY Integration for KenzySites

This directory contains the Bolt.DIY integration for the KenzySites landing page builder.

## Setup Instructions

### Option 1: Using Docker (Recommended)

```bash
# From the root directory
docker-compose -f docker-compose.full.yml up boltdiy
```

### Option 2: Manual Setup

1. Clone Bolt.DIY (if available):
```bash
git clone https://github.com/stackblitz/bolt.new.git .
# or
git clone https://github.com/stackblitz/bolt.git .
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The Bolt.DIY editor will be available at http://localhost:5173

## API Integration

The backend integrates with Bolt.DIY through two parallel implementations:

### V1 API (Mock Implementation)
- **Endpoint**: `/api/v1/landing-pages/*`
- **Implementation**: Simulated drag-and-drop
- **Use Case**: Fast, lightweight, no dependencies

### V2 API (Real Bolt.DIY)
- **Endpoint**: `/api/v2/landing-pages/*`
- **Implementation**: Real visual editor with Bolt.DIY
- **Use Case**: Full features, visual editing, live preview

## Switching Between Implementations

Set the environment variable:
```bash
# Use Bolt.DIY (default)
LANDING_PAGE_ENGINE=boltdiy

# Use mock implementation
LANDING_PAGE_ENGINE=mock
```

## Features Comparison

| Feature | V1 (Mock) | V2 (Bolt.DIY) |
|---------|-----------|---------------|
| Visual Editor | ❌ | ✅ |
| Live Preview | ❌ | ✅ |
| Drag & Drop | Simulated | Real |
| Code Export | Basic HTML | Full React/Vue/HTML |
| Resource Usage | Low | Medium |
| Dependencies | None | Node.js 20+ |

## Project Structure

```
boltdiy/
├── Dockerfile          # Docker container setup
├── projects/          # Saved projects (volume)
└── README.md          # This file
```

## Troubleshooting

### Bolt.DIY not starting
- Check if port 5173 is available
- Ensure Node.js 20+ is installed
- Check Docker logs: `docker logs kenzysites-boltdiy`

### Cannot connect from backend
- Ensure both services are on the same Docker network
- Check BOLTDIY_URL environment variable
- Verify Bolt.DIY health: `curl http://localhost:5173`

## Development

To modify the Bolt.DIY integration:

1. Edit `backend/app/services/boltdiy_integration.py`
2. Update API routes in `backend/app/api/routers/landing_pages_v2.py`
3. Restart the backend service

## Notes

- Bolt.DIY runs in WebContainers (browser-based Node.js)
- Best performance in Chrome/Edge browsers
- Projects are saved in the `projects/` volume
- Supports React, Vue, Vanilla JS, and more frameworks