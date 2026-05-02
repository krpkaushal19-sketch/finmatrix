#!/usr/bin/env python3
"""
FinMatrix - Complete Financial Intelligence Platform
One-click launcher for the entire application
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading

def main():
    print("=" * 60)
    print("💰 FINMATRIX - Financial Intelligence Platform")
    print("=" * 60)
    print("📐 Powered by PageRank Power Method (Linear Algebra Module 3)")
    print("=" * 60)
    
    # Get the directory where this script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    frontend_file = os.path.join(base_dir, "frontend", "index.html")
    
    # Check if backend exists
    if not os.path.exists(backend_dir):
        print("❌ Error: 'backend' folder not found!")
        print("   Please ensure the folder structure is correct.")
        return
    
    # Check if frontend exists
    if not os.path.exists(frontend_file):
        print("❌ Error: 'frontend/index.html' not found!")
        return
    
    print("\n📦 Installing dependencies...")
    req_file = os.path.join(backend_dir, "requirements.txt")
    if os.path.exists(req_file):
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], 
                       capture_output=True)
    else:
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors", "numpy"], 
                       capture_output=True)
    
    print("\n🚀 Starting Flask Backend Server...")
    print("   Server will run at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server\n")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open(f"file://{frontend_file}")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the Flask app
    os.chdir(backend_dir)
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")

if __name__ == "__main__":
    main()