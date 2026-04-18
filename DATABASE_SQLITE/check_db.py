import sqlite3
import sys
import os

# Use relative path from DATABASE_SQLITE folder
db_path = os.path.join(os.path.dirname(__file__), 'fitfinder.db')
print(f"Checking database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # List tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in c.fetchall()]
    print("=== FitFinder Database Tables ===")
    print("Tables:", ', '.join(tables))
    print()
    
    # Count entries in main tables
    main_tables = ['users', 'user_profiles', 'saved_outfits', 'try_on_history', 'outfits', 'contact_messages']
    print("=== Entry Counts ===")
    for table in main_tables:
        if table in tables:
            c.execute(f"SELECT COUNT(*) FROM {table}")
            count = c.fetchone()[0]
            print(f"{table}: {count}")
        else:
            print(f"{table}: 0 (table missing)")
    
    # Sample data from users
    print("\n=== Sample Users (top 3) ===")
    c.execute("SELECT id, userid, role FROM users LIMIT 3")
    users = c.fetchall()
    if users:
        for user in users:
            print(f"  ID:{user[0]} {user[1]} ({user[2]})")
    else:
        print("  No users found")
    
    # Sample history
    print("\n=== Recent History (top 3) ===")
    c.execute("SELECT id, garment_type, created_at FROM try_on_history ORDER BY created_at DESC LIMIT 3")
    history = c.fetchall()
    if history:
        for h in history:
            print(f"  ID:{h[0]} Type:{h[1]} Time:{h[2]}")
    else:
        print("  No history found")
    
    conn.close()
    print("\n✅ Database check complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")

