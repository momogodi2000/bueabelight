#!/usr/bin/env python
"""
BueaDelights Development Server
Runs Django and Tailwind CSS in parallel with hot reload
"""

import os
import sys
import subprocess
import threading
import time
import signal
from pathlib import Path

class BueaDelightsDevServer:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).resolve().parent
        
    def print_banner(self):
        """Print startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                        🍽️ BueaDelights                        ║
║                 "Local Flavors at Your Fingertips"          ║
║                                                              ║
║                    Development Server                        ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting development environment...
📱 Django Server: http://localhost:8000
🎨 Tailwind CSS: Watching for changes...
🔄 Hot Reload: Enabled
📧 Admin Panel: http://localhost:8000/admin/
🛒 API Endpoints: http://localhost:8000/api/

Press Ctrl+C to stop all services
        """
        print(banner)
        
    def check_requirements(self):
        """Check if required tools are installed"""
        print("🔍 Checking requirements...")
        
        # Check Python
        try:
            import django
            print(f"✅ Django {django.get_version()} installed")
        except ImportError:
            print("❌ Django not installed. Run: pip install -r requirements.txt")
            return False
            
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Node.js {result.stdout.strip()} installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Node.js not installed. Please install Node.js")
            return False
            
        # Check npm packages
        if not (self.base_dir / 'node_modules').exists():
            print("📦 Installing npm packages...")
            try:
                subprocess.run(['npm', 'install'], cwd=self.base_dir, check=True)
                print("✅ npm packages installed")
            except subprocess.CalledProcessError:
                print("❌ Failed to install npm packages")
                return False
        else:
            print("✅ npm packages already installed")
            
        return True
        
    def run_django(self):
        """Run Django development server"""
        print("🐍 Starting Django server...")
        
        # Set environment variables
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'bueadelights.settings'
        env['DEBUG'] = 'True'
        
        try:
            # Run migrations first
            print("📊 Running database migrations...")
            subprocess.run([
                sys.executable, 'manage.py', 'migrate'
            ], cwd=self.base_dir, check=True, env=env)
            
            # Create super admins
            print("👤 Creating super admin users...")
            subprocess.run([
                sys.executable, 'manage.py', 'create_superadmins'
            ], cwd=self.base_dir, env=env)
            
            # Collect static files
            print("📁 Collecting static files...")
            subprocess.run([
                sys.executable, 'manage.py', 'collectstatic', '--noinput'
            ], cwd=self.base_dir, check=True, env=env)
            
            # Start Django server
            process = subprocess.Popen([
                sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'
            ], cwd=self.base_dir, env=env)
            
            self.processes.append(process)
            print("✅ Django server started on http://127.0.0.1:8000")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error starting Django: {e}")
            return False
            
        return True
        
    def run_tailwind(self):
        """Run Tailwind CSS build process"""
        print("🎨 Starting Tailwind CSS watcher...")
        
        try:
            process = subprocess.Popen([
                'npm', 'run', 'build-css'
            ], cwd=self.base_dir)
            
            self.processes.append(process)
            print("✅ Tailwind CSS watcher started")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error starting Tailwind CSS: {e}")
            return False
            
        return True
        
    def setup_signal_handlers(self):
        """Setup signal handlers for clean shutdown"""
        def signal_handler(sig, frame):
            print("\n🛑 Shutting down development server...")
            self.cleanup()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def cleanup(self):
        """Cleanup all processes"""
        print("🧹 Cleaning up processes...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            except Exception as e:
                print(f"Error cleaning up process: {e}")
                
    def monitor_processes(self):
        """Monitor all processes and restart if needed"""
        while True:
            time.sleep(5)
            
            for i, process in enumerate(self.processes):
                if process.poll() is not None:
                    print(f"⚠️  Process {i} died, attempting restart...")
                    # You could implement restart logic here
                    
    def run(self):
        """Main run method"""
        try:
            self.print_banner()
            
            if not self.check_requirements():
                return False
                
            self.setup_signal_handlers()
            
            # Start services in separate threads
            django_thread = threading.Thread(target=self.run_django, daemon=True)
            tailwind_thread = threading.Thread(target=self.run_tailwind, daemon=True)
            
            django_thread.start()
            time.sleep(2)  # Give Django time to start
            
            tailwind_thread.start()
            time.sleep(1)  # Give Tailwind time to start
            
            print("\n🎉 Development server is ready!")
            print("🌐 Open your browser to: http://localhost:8000")
            print("🔑 Admin panel: http://localhost:8000/admin/")
            print("\nSuper Admin Credentials:")
            print("1. Username: folefack_caroline | Password: BueaDelights2025!Caroline")
            print("2. Username: momo_godi_yvan | Password: BueaDelights2025!Yvan") 
            print("3. Username: momo_marlyse | Password: BueaDelights2025!Marlyse")
            print("\n⚠️  Remember to change these passwords in production!")
            print("\nPress Ctrl+C to stop the server")
            
            # Wait for threads to complete (they won't unless there's an error)
            django_thread.join()
            tailwind_thread.join()
            
        except KeyboardInterrupt:
            print("\n🛑 Received shutdown signal...")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            self.cleanup()
            
        return True

def main():
    """Main entry point"""
    server = BueaDelightsDevServer()
    success = server.run()
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())