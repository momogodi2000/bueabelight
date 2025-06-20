#!/usr/bin/env python
"""
BueaDelights Setup Script
Complete setup and initialization for the BueaDelights Django application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class BueaDelightsSetup:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.python_executable = sys.executable
        
    def print_header(self):
        """Print setup header"""
        header = """
╔══════════════════════════════════════════════════════════════╗
║                        🍽️ BueaDelights                        ║
║                 "Local Flavors at Your Fingertips"          ║
║                                                              ║
║                      Setup & Installation                    ║
╚══════════════════════════════════════════════════════════════╝

🚀 Setting up your BueaDelights Django application...
        """
        print(header)
    
    def check_python_version(self):
        """Check Python version"""
        print("🐍 Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ is required")
            print(f"Current version: {version.major}.{version.minor}.{version.micro}")
            return False
        
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    
    def check_node_version(self):
        """Check Node.js version"""
        print("📦 Checking Node.js version...")
        
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            print(f"✅ Node.js {version} - OK")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Node.js is required but not installed")
            print("Please install Node.js from https://nodejs.org/")
            return False
    
    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist"""
        print("🔧 Setting up virtual environment...")
        
        venv_path = self.base_dir / 'venv'
        
        if venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        try:
            subprocess.run([
                self.python_executable, '-m', 'venv', 'venv'
            ], cwd=self.base_dir, check=True)
            
            print("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get path to Python executable in virtual environment"""
        if os.name == 'nt':  # Windows
            return self.base_dir / 'venv' / 'Scripts' / 'python.exe'
        else:  # Unix/Linux/Mac
            return self.base_dir / 'venv' / 'bin' / 'python'
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        print("📚 Installing Python dependencies...")
        
        venv_python = self.get_venv_python()
        
        if not venv_python.exists():
            print("❌ Virtual environment Python not found")
            return False
        
        try:
            # Upgrade pip first
            subprocess.run([
                str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'
            ], cwd=self.base_dir, check=True)
            
            # Install requirements
            subprocess.run([
                str(venv_python), '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], cwd=self.base_dir, check=True)
            
            print("✅ Python dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            return False
    
    def install_node_dependencies(self):
        """Install Node.js dependencies"""
        print("🎨 Installing Node.js dependencies...")
        
        try:
            subprocess.run(['npm', 'install'], cwd=self.base_dir, check=True)
            print("✅ Node.js dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Node.js dependencies: {e}")
            return False
    
    def create_env_file(self):
        """Create .env file if it doesn't exist"""
        print("⚙️  Setting up environment configuration...")
        
        env_file = self.base_dir / '.env'
        
        if env_file.exists():
            print("✅ .env file already exists")
            return True
        
        env_content = '''# BueaDelights Environment Configuration
# Django Settings
SECRET_KEY=django-insecure-change-me-in-production-very-long-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# WhatsApp Configuration
WHATSAPP_NUMBER=+237699808260
BUSINESS_NAME=BueaDelights
BUSINESS_EMAIL=info@bueadelights.com

# Payment Configuration
NOUPIA_API_KEY=your-noupia-api-key
NOUPIA_MERCHANT_ID=your-merchant-id
DELIVERY_FEE=1500

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
'''
        
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("✅ .env file created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    
    def create_directories(self):
        """Create necessary directories"""
        print("📁 Creating necessary directories...")
        
        directories = [
            'static/css',
            'static/js', 
            'static/images',
            'media',
            'logs',
            'staticfiles'
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print("✅ Directories created successfully")
        return True
    
    def build_css(self):
        """Build Tailwind CSS"""
        print("🎨 Building Tailwind CSS...")
        
        try:
            subprocess.run([
                'npm', 'run', 'build-css-prod'
            ], cwd=self.base_dir, check=True)
            print("✅ CSS built successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build CSS: {e}")
            return False
    
    def run_django_setup(self):
        """Run Django setup commands"""
        print("🗄️  Setting up Django application...")
        
        venv_python = self.get_venv_python()
        
        commands = [
            ['migrate'],
            ['create_superadmins'],
            ['create_sample_data'],
            ['collectstatic', '--noinput']
        ]
        
        for command in commands:
            try:
                print(f"   Running: python manage.py {' '.join(command)}")
                subprocess.run([
                    str(venv_python), 'manage.py'
                ] + command, cwd=self.base_dir, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to run {command[0]}: {e}")
                return False
        
        print("✅ Django setup completed successfully")
        return True
    
    def create_test_script(self):
        """Create test script"""
        print("🧪 Creating test script...")
        
        test_script_content = '''#!/usr/bin/env python
"""Test script for BueaDelights"""

import os
import sys
import django
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bueadelights.settings')
django.setup()

def run_tests():
    """Run all tests"""
    print("🧪 Running BueaDelights tests...")
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'test'])

if __name__ == '__main__':
    run_tests()
'''
        
        test_script = self.base_dir / 'run_tests.py'
        
        try:
            with open(test_script, 'w') as f:
                f.write(test_script_content)
            test_script.chmod(0o755)
            print("✅ Test script created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create test script: {e}")
            return False
    
    def print_success_message(self):
        """Print success message with instructions"""
        success_message = """
╔══════════════════════════════════════════════════════════════╗
║                      🎉 Setup Complete!                      ║
╚══════════════════════════════════════════════════════════════╝

✅ BueaDelights has been set up successfully!

🚀 Quick Start:
   1. Activate virtual environment:
      • Windows: venv\\Scripts\\activate
      • Mac/Linux: source venv/bin/activate
   
   2. Start development server:
      python dev_server.py
   
   3. Open your browser:
      http://localhost:8000

🔑 Admin Access:
   • URL: http://localhost:8000/admin/
   • Username: folefack_caroline
   • Password: BueaDelights2025!Caroline
   
   Additional accounts: momo_godi_yvan, momo_marlyse

📱 Key Features:
   • Product catalog with Cameroonian dishes
   • Shopping cart and checkout
   • WhatsApp integration (+237 6 99 80 82 60)
   • Mobile money payment (Noupia)
   • Admin dashboard with analytics
   • Catering service requests

🛠️  Development Commands:
   • Run tests: python run_tests.py
   • Create superuser: python manage.py create_superadmins
   • Add sample data: python manage.py create_sample_data
   • Collect static: python manage.py collectstatic

📧 Configuration:
   • Edit .env file for email and payment settings
   • Configure business settings in admin panel
   • Update WhatsApp number in settings

🌐 Production Deployment:
   • See README.md for Render.com deployment
   • Use build.sh for production builds
   • Configure environment variables

📞 Support:
   • Documentation: README.md
   • Issues: GitHub Issues
   • Contact: info@bueadelights.com

🍽️ "Local Flavors at Your Fingertips" - BueaDelights Team
        """
        print(success_message)
    
    def run_setup(self):
        """Run complete setup process"""
        self.print_header()
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking Node.js version", self.check_node_version),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Installing Node.js dependencies", self.install_node_dependencies),
            ("Creating environment configuration", self.create_env_file),
            ("Creating directories", self.create_directories),
            ("Building CSS", self.build_css),
            ("Setting up Django", self.run_django_setup),
            ("Creating test script", self.create_test_script),
        ]
        
        for step_name, step_function in steps:
            print(f"\n📋 {step_name}...")
            
            if not step_function():
                print(f"\n❌ Setup failed at: {step_name}")
                print("Please check the error messages above and try again.")
                return False
        
        self.print_success_message()
        return True

def main():
    """Main entry point"""
    setup = BueaDelightsSetup()
    success = setup.run_setup()
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())