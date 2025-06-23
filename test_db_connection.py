#!/usr/bin/env python
"""
Test PostgreSQL database connection before deployment
Run this locally to verify your database credentials work
"""

import os
import psycopg2
from decouple import config

def test_database_connection():
    """Test connection to PostgreSQL database"""
    
    print("🔍 Testing PostgreSQL Database Connection...")
    print("=" * 50)
    
    # Get database credentials
    db_name = config('DB_NAME', default='bueadelights')
    db_user = config('DB_USER', default='bueadelights_user')
    db_password = config('DB_PASSWORD', default='')
    db_host = config('DB_HOST', default='')
    db_port = config('DB_PORT', default='5432')
    
    print(f"📍 Host: {db_host}")
    print(f"📍 Database: {db_name}")
    print(f"📍 User: {db_user}")
    print(f"📍 Port: {db_port}")
    print("=" * 50)
    
    if not db_host or not db_password:
        print("❌ Missing database credentials!")
        print("Please set DB_HOST and DB_PASSWORD in your .env file")
        return False
    
    try:
        # Test connection
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port,
            connect_timeout=10
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        
        print("✅ Database connection successful!")
        print(f"✅ PostgreSQL version: {db_version[0][:100]}...")
        
        # Test creating a table (and drop it)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100)
            );
        ''')
        
        cursor.execute('DROP TABLE test_table;')
        conn.commit()
        
        print("✅ Database permissions: OK (can create/drop tables)")
        
        cursor.close()
        conn.close()
        
        print("=" * 50)
        print("🎉 All database tests passed!")
        print("✅ Ready for deployment!")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Possible issues:")
        print("   - Wrong host/port")
        print("   - Wrong username/password")
        print("   - Database not accessible from your IP")
        print("   - Firewall blocking connection")
        return False
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()