#!/bin/bash

# Guidance Blueprint Kit Pro - Startup Script

echo "🚀 Starting Guidance Blueprint Kit Pro Web Application"
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.7+ and try again."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found. Please run this script from the web_app directory."
    exit 1
fi

# Check if GuidanceBlueprintKit-Pro exists
if [ ! -d "../GuidanceBlueprintKit-Pro" ]; then
    echo "❌ GuidanceBlueprintKit-Pro directory not found."
    echo "Please ensure the GuidanceBlueprintKit-Pro directory exists in the parent directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p static templates

echo "✅ Setup complete!"
echo ""
echo "🌐 Starting web server..."
echo "📍 Application will be available at: http://localhost:8000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the application
python main.py
