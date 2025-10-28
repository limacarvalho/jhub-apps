# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JupyterHub Apps Launcher is a JupyterHub extension that enables users to launch multiple web application frameworks (Panel, Bokeh, Streamlit, Plotly Dash, Voila, Gradio, JupyterLab, and custom Python commands) through a unified interface. The project consists of a Python FastAPI backend that integrates with JupyterHub and a React TypeScript frontend.

## Development Commands

### Python Backend Development
```bash
# Install dependencies
uv sync --extra dev

# Start JupyterHub backend (required for development)
export JHUB_APP_JWT_SECRET_KEY=$(openssl rand -hex 32)
jupyterhub -f jupyterhub_config.py

# Run tests
pytest jhub_apps/tests                          # Unit tests
pytest jhub_apps/tests/tests_e2e -vvv -s --headed  # E2E tests
pytest -m "not k3s" jhub_apps/tests            # Skip k3s-specific tests

# CLI tool
japps --version
```

### React Frontend Development (from `ui/` directory)
```bash
# Install dependencies
npm install

# Development build with hot reload (run in separate terminal from backend)
npm run watch

# Production build
npm run build

# Development build
npm run build:dev

# Testing and code quality
npm test                                      # Run tests
npm run test:coverage                         # Test coverage
npm run lint                                  # ESLint with auto-fix
npm run format                                # Prettier formatting
```

### Kubernetes Development (from `k3s-dev/` directory)
```bash
# Setup local k3s cluster with Tilt for development
make up    # Start environment (access at http://localhost:8000)
make down  # Tear down environment
make clean # Clean everything
```

### Docker Development
```bash
# Build and run with Docker Compose
docker compose build
docker compose up

# Build JupyterHub image
docker build -t jhub -f Dockerfile.jhub .
```

## Architecture Overview

### Core Components

**Backend (Python/FastAPI)**:
- `jhub_apps/service/` - FastAPI application with REST API and web UI routes
- `jhub_apps/spawner/` - Custom JupyterHub spawner implementations for different frameworks
- `jhub_apps/hub_client/` - JupyterHub API client for server management
- `jhub_apps/configuration.py` - JupyterHub extension setup and configuration

**Frontend (React/TypeScript)**:
- `ui/src/` - React application with Material-UI components
- Uses React Query for API state management and Recoil for client state
- Vite for build tooling with TypeScript support

**Framework Support System**:
- Template-based command generation in `jhub_apps/spawner/command.py`
- Framework definitions in `jhub_apps/spawner/types.py`
- Extensible architecture for adding new frameworks

### Key Architectural Patterns

1. **JupyterHub Integration**: Runs as a JupyterHub service with OAuth authentication
2. **Plugin-based Framework Support**: Each framework has specific command templates and configurations
3. **Multi-tenancy**: User and group-based sharing with role-based access control
4. **Configuration-Driven**: Uses JupyterHub traitlets for flexible deployment

### Development Workflow

**Local Development** requires two terminals:
1. Backend: `jupyterhub -f jupyterhub_config.py` (JupyterHub with FastAPI service)
2. Frontend: `cd ui && npm run watch` (React development server)

**API Documentation**: Available at http://127.0.0.1:10202/services/japps/docs when JupyterHub is running

**Authentication**: Uses OAuth2 with JupyterHub - set `JHUB_APP_JWT_SECRET_KEY` environment variable for development

### Testing Strategy

- **Unit Tests**: pytest for Python components
- **E2E Tests**: Playwright for full user workflow testing
- **UI Tests**: Vitest for React component testing
- **Kubernetes Tests**: Specialized tests for k3d deployment environment (marked with `k3s` marker)

### Configuration

Key configuration is handled through `JAppsConfig` in JupyterHub's config file:
- `apps_auth_type`: Authentication method for apps ("oauth" or "none")
- `python_exec`: Python executable path
- `jupyterhub_config_path`: Path to JupyterHub config
- `conda_envs`: Conda environments for app creation

### Dependencies and Tools

- **Python**: uv for package management, ruff for linting, pytest for testing
- **React**: npm, Vite, TypeScript, Material-UI, ESLint, Prettier
- **Development**: Docker, Kubernetes (k3d), Tilt for rapid development
- **CI/CD**: GitHub Actions with multi-Python version testing (3.8-3.12)