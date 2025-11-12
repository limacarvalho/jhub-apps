#!/bin/bash
# JHub Apps - Complete Build Script
#
# This script automates the complete build process for JHub Apps:
# 1. Builds the React/TypeScript frontend
# 2. Copies static assets to the Python package
# 3. Creates Python wheel and source distribution packages
#
# Usage:
#   ./build.sh
#
# Output:
#   dist/jhub_apps-<version>-py3-none-any.whl  (installable wheel)
#   dist/jhub_apps-<version>.tar.gz            (source distribution)
#
# Requirements:
#   - Node.js 20.x or higher
#   - npm 10.x or higher
#   - uv (available at $HOME/.local/bin/uv)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print banner
echo "================================================"
echo "  JHub Apps - Package Build Script"
echo "================================================"
echo ""

# Check prerequisites
log_info "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed. Please install Node.js 20.x or higher."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    log_error "npm is not installed. Please install npm."
    exit 1
fi

# Set uv path
UV_CMD="$HOME/.local/bin/uv"

if ! command -v "$UV_CMD" &> /dev/null; then
    log_error "uv is not installed at $UV_CMD. Please install uv."
    exit 1
fi

log_success "All prerequisites found"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    log_error "pyproject.toml not found. Please run this script from the repository root."
    exit 1
fi

if [ ! -d "ui" ]; then
    log_error "ui/ directory not found. Please run this script from the repository root."
    exit 1
fi

# Clean previous builds
log_info "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info
rm -rf ui/dist/
log_success "Cleaned build directories"
echo ""

# Build frontend
log_info "Building frontend..."
cd ui

# Install npm dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    log_info "Installing npm dependencies (this may take a few minutes)..."
    npm install
    log_success "npm dependencies installed"
else
    log_info "npm dependencies already installed"
fi

# Build the UI
log_info "Running TypeScript compiler and Vite build..."
npm run build

if [ $? -ne 0 ]; then
    log_error "Frontend build failed"
    exit 1
fi

log_success "Frontend built successfully"

# Copy assets to static folder
log_info "Copying built assets to static folder..."
./build-and-copy.sh

if [ $? -ne 0 ]; then
    log_error "Failed to copy assets"
    exit 1
fi

log_success "Assets copied to jhub_apps/static/"
cd ..
echo ""

# Verify static files exist
log_info "Verifying static files..."
if [ ! -f "jhub_apps/static/js/index.js" ]; then
    log_error "jhub_apps/static/js/index.js not found after build"
    exit 1
fi

if [ ! -f "jhub_apps/static/css/index.css" ]; then
    log_error "jhub_apps/static/css/index.css not found after build"
    exit 1
fi

log_success "Static files verified"
echo ""

# Build Python package with uv
log_info "Building Python wheel and source distribution with uv..."
"$UV_CMD" build

if [ $? -ne 0 ]; then
    log_error "Python package build failed"
    exit 1
fi

log_success "Python packages built successfully"
echo ""

# List built packages
log_info "Built packages:"
ls -lh dist/
echo ""

# Final summary
echo "================================================"
log_success "Build completed successfully!"
echo "================================================"
echo ""
echo "Distribution packages created in: dist/"
echo ""
echo "Next steps:"
echo "  - Test installation: pip install dist/*.whl"
echo "  - Upload to PyPI: python -m twine upload dist/*"
echo ""
