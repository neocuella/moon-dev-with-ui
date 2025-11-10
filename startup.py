#!/usr/bin/env python3

"""
🚀 Moon Dev Flow UI - Cross-Platform Startup Script

This script sets up and starts both the FastAPI backend and React frontend.
Works on macOS, Linux, and Windows.

Usage:
  python startup.py
"""

import os
import sys
import subprocess
import shutil
import time
import signal
import platform
from pathlib import Path
from typing import Optional, List

# Colors
class Colors:
    HEADER = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def disable():
        Colors.HEADER = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''


def is_windows():
    return platform.system() == "Windows"


def print_header():
    """Print welcome header"""
    print(f"{Colors.HEADER}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  🌙 Moon Dev Flow UI - Startup Script                   ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")


def check_command(cmd: str, name: str) -> bool:
    """Check if a command is available"""
    return shutil.which(cmd) is not None


def check_python() -> bool:
    """Check Python version"""
    print(f"{Colors.WARNING}[1/5] Checking prerequisites...{Colors.ENDC}")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"{Colors.FAIL}✗ Python 3.10+ required (found {version.major}.{version.minor}){Colors.ENDC}")
        return False
    
    print(f"{Colors.OKGREEN}✓ Python {version.major}.{version.minor}.{version.micro} found{Colors.ENDC}")
    return True


def check_node() -> bool:
    """Check Node.js installation"""
    if not check_command("node", "Node.js"):
        print(f"{Colors.FAIL}✗ Node.js not found. Please install Node.js 18+{Colors.ENDC}")
        return False
    
    result = subprocess.run(["node", "--version"], capture_output=True, text=True)
    version = result.stdout.strip()
    print(f"{Colors.OKGREEN}✓ {version} found{Colors.ENDC}")
    return True


def check_postgres() -> bool:
    """Check PostgreSQL connection"""
    try:
        result = subprocess.run(
            ["psql", "-h", "localhost", "-U", "postgres", "-tc", "SELECT 1"],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            print(f"{Colors.OKGREEN}✓ PostgreSQL is running{Colors.ENDC}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print(f"{Colors.WARNING}⚠ PostgreSQL not responding on localhost{Colors.ENDC}")
    print(f"{Colors.WARNING}   Start with: docker run -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:14{Colors.ENDC}")
    return False


def setup_backend() -> bool:
    """Setup backend environment"""
    print(f"\n{Colors.WARNING}[2/5] Setting up backend...{Colors.ENDC}")
    
    backend_dir = Path("backend")
    venv_dir = backend_dir / ("venv" if not is_windows() else "venv")
    
    # Create venv if needed
    if not venv_dir.exists():
        print(f"{Colors.BOLD}Creating virtual environment...{Colors.ENDC}")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    
    # Install dependencies
    print(f"{Colors.BOLD}Installing dependencies...{Colors.ENDC}")
    pip_cmd = str(venv_dir / ("Scripts/pip" if is_windows() else "bin/pip"))
    requirements = backend_dir / "requirements.txt"
    
    if requirements.exists():
        subprocess.run([pip_cmd, "install", "-q", "-r", str(requirements)], check=True)
        print(f"{Colors.OKGREEN}✓ Backend setup complete{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.FAIL}✗ requirements.txt not found{Colors.ENDC}")
        return False


def setup_frontend() -> bool:
    """Setup frontend environment"""
    print(f"\n{Colors.WARNING}[3/5] Setting up frontend...{Colors.ENDC}")
    
    ui_dir = Path("ui")
    node_modules = ui_dir / "node_modules"
    
    if not node_modules.exists():
        print(f"{Colors.BOLD}Installing npm dependencies...{Colors.ENDC}")
        os.chdir(str(ui_dir))
        result = subprocess.run(["npm", "install", "-q"], capture_output=True)
        os.chdir("..")
        
        if result.returncode != 0:
            print(f"{Colors.FAIL}✗ npm install failed{Colors.ENDC}")
            return False
    
    print(f"{Colors.OKGREEN}✓ Frontend setup complete{Colors.ENDC}")
    return True


def start_backend() -> Optional[subprocess.Popen]:
    """Start FastAPI backend"""
    backend_dir = Path("backend")
    venv_dir = backend_dir / ("Scripts" if is_windows() else "bin")
    python_exe = venv_dir / ("python.exe" if is_windows() else "python")
    
    cmd = [
        str(python_exe),
        "-m", "uvicorn",
        "src.api.app:app",
        "--reload",
        "--host", "127.0.0.1",
        "--port", "8000"
    ]
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir)
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(backend_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"{Colors.OKGREEN}✓ Backend started (PID: {process.pid}){Colors.ENDC}")
        time.sleep(2)
        
        # Check health
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:8000/health", timeout=2)
            print(f"{Colors.OKGREEN}✓ Backend health check passed{Colors.ENDC}")
        except:
            print(f"{Colors.WARNING}⚠ Backend is running but health check failed{Colors.ENDC}")
        
        return process
    except Exception as e:
        print(f"{Colors.FAIL}✗ Failed to start backend: {e}{Colors.ENDC}")
        return None


def start_frontend() -> Optional[subprocess.Popen]:
    """Start React frontend"""
    ui_dir = Path("ui")
    
    cmd = ["npm", "run", "dev"]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(ui_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"{Colors.OKGREEN}✓ Frontend started (PID: {process.pid}){Colors.ENDC}")
        time.sleep(3)
        return process
    except Exception as e:
        print(f"{Colors.FAIL}✗ Failed to start frontend: {e}{Colors.ENDC}")
        return None


def main():
    """Main startup logic"""
    print_header()
    
    # Check prerequisites
    if not check_python():
        return 1
    
    if not check_node():
        return 1
    
    check_postgres()
    
    # Setup environments
    if not setup_backend():
        return 1
    
    if not setup_frontend():
        return 1
    
    # Start services
    print(f"\n{Colors.WARNING}[4/5] Starting services...{Colors.ENDC}\n")
    print(f"{Colors.OKGREEN}═══════════════════════════════════════════════════════")
    print(f"Starting backend on http://localhost:8000")
    print(f"Starting frontend on http://localhost:5173")
    print(f"═══════════════════════════════════════════════════════{Colors.ENDC}\n")
    
    backend_process = start_backend()
    if not backend_process:
        return 1
    
    frontend_process = start_frontend()
    if not frontend_process:
        if backend_process:
            backend_process.terminate()
        return 1
    
    # Print success message
    print(f"\n{Colors.OKGREEN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  ✅ Both services are running!                          ║")
    print("║                                                          ║")
    print("║  Backend:  http://localhost:8000                        ║")
    print("║  Frontend: http://localhost:5173                        ║")
    print("║  API Docs: http://localhost:8000/docs                   ║")
    print("║                                                          ║")
    print("║  Press Ctrl+C to stop both services                     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print(f"\n{Colors.WARNING}Stopping services...{Colors.ENDC}")
        backend_process.terminate()
        frontend_process.terminate()
        
        try:
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
            frontend_process.kill()
        
        print(f"{Colors.OKGREEN}✓ Services stopped{Colors.ENDC}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Wait for both processes
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)
    
    return 0


if __name__ == "__main__":
    # Disable colors on Windows if terminal doesn't support them
    if is_windows() and not os.getenv("TERM"):
        Colors.disable()
    
    sys.exit(main())
