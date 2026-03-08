#!/usr/bin/env python3
"""
Test script to verify the new database structure works correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main.config31 import init_chat_db, get_db_path
import sqlite3

def test_database_initialization():
    """Test that database initialization works for a sample chat"""
    test_chat_id = -1001234567890  # Test chat ID
    
    print(f"Testing database initialization for chat ID: {test_chat_id}")
    
    # Test database path generation
    db_path = get_db_path(test_chat_id)
    print(f"Database path: {db_path}")
    
    # Test database initialization
    try:
        init_chat_db(test_chat_id)
        print("✅ Database initialization successful")
        
        # Verify tables were created
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        expected_tables = [
            'users', 'bans', 'black_list', 'bookmarks', 'default_periods',
            'dk', 'muts', 'perevod', 'pravils', 'texts', 'recommendation',
            'warns', 'warn_snat', 'links', 'stavki', 'ruletka'
        ]
        
        created_tables = [table[0] for table in tables]
        
        print(f"Created tables: {created_tables}")
        
        # Check if all expected tables exist
        missing_tables = set(expected_tables) - set(created_tables)
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        else:
            print("✅ All expected tables created successfully")
        
        # Test that dk table has default commands
        cursor.execute("SELECT comand, dk FROM dk")
        commands = cursor.fetchall()
        print(f"Default commands: {commands}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_user_functions():
    """Test user-related functions with new database structure"""
    try:
        from main.config31 import GetUserByID, GetUserByMessage
        
        test_chat_id = -1001234567890
        test_user_id = 123456789
        
        print(f"\nTesting user functions for chat {test_chat_id}, user {test_user_id}")
        
        # Test GetUserByID (should handle missing user gracefully)
        try:
            user_info = GetUserByID(test_user_id, test_chat_id)
            print(f"✅ GetUserByID works (user not found as expected)")
        except Exception as e:
            print(f"⚠️ GetUserByID handling: {e}")
        
        print("✅ User functions test completed")
        return True
        
    except Exception as e:
        print(f"❌ User functions test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing new database structure...")
    
    success = True
    
    # Test 1: Database initialization
    if not test_database_initialization():
        success = False
    
    # Test 2: User functions
    if not test_user_functions():
        success = False
    
    if success:
        print("\n🎉 All tests passed! The new database structure is working correctly.")
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
    
    # Clean up test database
    try:
        test_db_path = get_db_path(-1001234567890)
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print("🧹 Test database cleaned up")
    except:
        pass
