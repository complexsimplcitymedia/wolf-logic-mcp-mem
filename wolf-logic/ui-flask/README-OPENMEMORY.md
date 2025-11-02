# OpenMemory Flask UI

A modern, feature-rich web interface for OpenMemory built with Flask and Berry Bootstrap 5 template. This UI provides a complete management interface for your AI memory layer.

## Features

- **Dashboard**: Overview of memories and apps with real-time stats
- **Memory Management**: Create, view, edit, delete, pause, and archive memories
- **Advanced Filtering**: Search by text, filter by app, category, state
- **Bulk Operations**: Manage multiple memories at once
- **App Management**: View and manage all applications using your memories
- **Access Logs**: Track when and how memories are accessed
- **Related Memories**: Discover related memories based on shared categories
- **Export/Import**: Backup and restore your memories
- **Settings**: Configure LLM and embedder settings
- **Beautiful UI**: Modern, responsive design with Berry Bootstrap 5

## Quick Start

### Using Docker Compose (Recommended)

1. Set environment variables:
```bash
export OLLAMA_URL=your-api-key
export USER_ID=your-user-id
```

2. Start the full stack:
```bash
cd /mnt/s/wolf-logic/wolf-logic/ui-flask
docker-compose up -d
```

3. Access the UI at http://localhost:5000

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`

3. Run the application:
```bash
python run.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `True` |
| `MEMORY_API_URL` | OpenMemory backend URL | `http://openmemory-mcp:8765` |
| `USER_ID` | User identifier | `default-user` |
| `SECRET_KEY` | Flask secret key | `openmemory-secret-key-change-in-production` |

## Project Structure

```
ui-flask/
├── apps/
│   ├── memories/             # Memory management blueprint
│   │   ├── routes.py         # Route handlers
│   │   └── api_client.py     # Backend API client
├── templates/
│   ├── memories/             # Memory UI templates
│   │   ├── dashboard.html
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── ...
│   └── includes/
│       └── sidebar-memory.html
├── static/                   # CSS, JS, images
└── run.py                    # Entry point
```

## Available Routes

- `/` - Dashboard
- `/memories` - List memories
- `/memories/create` - Create memory
- `/memories/<id>` - View details
- `/apps` - List applications
- `/settings` - Configuration
- `/export` - Export backup
