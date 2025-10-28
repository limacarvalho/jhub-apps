# Build and Deployment Instructions

This document provides instructions for building and deploying jhub-apps with the latest frontend changes.

## Quick Overview

jhub-apps consists of:
- **Python Backend**: FastAPI service that integrates with JupyterHub
- **React Frontend**: TypeScript/React UI that gets compiled into static assets
- **Distribution**: Pre-built frontend assets are included in the Python package

## Development Workflow

### Prerequisites
```bash
# Python dependencies
uv sync --extra dev

# Node.js dependencies (for frontend)
cd ui/
npm install
cd ..
```

### Building the Frontend
```bash
cd ui/
npm run build
cd ..
```

The build process:
1. Compiles TypeScript to JavaScript (`tsc`)
2. Bundles React application with Vite
3. Outputs optimized assets to `ui/dist/`
4. Pre-commit hooks automatically commit these built files

## Production Deployment Options

### Option 1: Git Install (Easiest)
Install directly from the Git repository (includes pre-built assets):

```bash
pip uninstall jhub-apps
pip install -U git+https://github.com/limacarvalho/jhub-apps.git@main

# Restart JupyterHub
sudo systemctl restart jupyterhub
```

**Pros:** Always gets the latest version, no manual file handling
**Cons:** Slower, downloads and compiles on install

### Option 2: Pre-built Wheel File (Fastest)
Download and install a pre-compiled `.whl` file:

```bash
# Build the wheel locally (one-time setup)
cd /path/to/jhub-apps
python -m build

# This creates: dist/jhub_apps-VERSION-py3-none-any.whl

# Upload to production server and install
scp dist/jhub_apps-*.whl user@production-server:/tmp/
ssh user@production-server

# On production server
pip uninstall jhub-apps
pip install /tmp/jhub_apps-*.whl

# Restart JupyterHub
sudo systemctl restart jupyterhub
```

**Pros:** Fast installation, no network dependencies during install
**Cons:** Requires manual building and file transfer

### Option 3: Source Distribution (sdist)
Install from a source archive:

```bash
# Create source distribution
cd /path/to/jhub-apps
python -m build --sdist

# This creates: dist/jhub_apps-VERSION.tar.gz

# Upload and install
scp dist/jhub_apps-*.tar.gz user@production-server:/tmp/
ssh user@production-server

# On production server
pip uninstall jhub-apps
pip install /tmp/jhub_apps-*.tar.gz

# Restart JupyterHub
sudo systemctl restart jupyterhub
```

**Pros:** Smaller file size than wheel
**Cons:** Slightly slower installation than wheel

## Build Commands Reference

### Frontend Only
```bash
cd ui/
npm run build          # Production build
npm run build:dev      # Development build
npm run watch          # Development with hot reload
```

### Package Distribution
```bash
# Install build tools
pip install build

# Build both wheel and source distribution
python -m build

# Build only wheel
python -m build --wheel

# Build only source distribution
python -m build --sdist
```

Output files are created in `dist/` directory.

## Deployment Checklist

### Before Deploying
- [ ] Run `npm run build` in `ui/` directory
- [ ] Commit built assets to Git (pre-commit hook handles this)
- [ ] Test locally with JupyterHub

### Production Deployment
1. **Choose installation method** (Git, Wheel, or sdist)
2. **Backup current installation**
   ```bash
   pip list | grep jhub-apps  # Note current version
   ```
3. **Install new version**
4. **Restart JupyterHub**
5. **Verify new features work**
   - Check Custom Command dialog appears
   - Verify File Path field visibility changes
   - Test port placeholder guidance

## Troubleshooting

### Frontend Not Updating
If you don't see UI changes after deployment:
1. Clear browser cache
2. Check that built assets are updated:
   ```bash
   ls -la /opt/conda/lib/python3.9/site-packages/jhub_apps/static/js/
   ```
3. Verify JupyterHub restarted successfully

### Build Issues
If frontend build fails:
```bash
# Clean and rebuild
cd ui/
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Installation Issues
If pip install fails:
```bash
# Clean install
pip uninstall jhub-apps
pip install --no-cache-dir <package-file>
```

## Automation (Optional)

### GitHub Actions
The project includes GitHub Actions workflows that can automatically build and release packages. Check `.github/workflows/` for available automation.

### Docker builds
For containerized deployments:
```bash
# Build with frontend
docker build -t jhub-apps:latest .

# This automatically runs npm run build during Docker build
```

## File Structure

After installation, the frontend assets are located at:
```
/opt/conda/lib/python3.9/site-packages/jhub_apps/static/
├── js/
│   └── index.js          # Compiled React app
├── css/
│   └── index.css         # Compiled styles
└── assets/               # Static images and fonts
```

## Performance Notes

- **Git install**: Slower due to network transfer and build process
- **Wheel file**: Fastest installation, recommended for production
- **sdist**: Middle ground, smaller file size but requires unpacking

For production environments with multiple servers, build once and distribute the wheel file to all servers for consistent and fast deployments.
