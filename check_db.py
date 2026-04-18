import sqlite3
import sys

db_path = 'DATABASE_SQLITE/fitfinder.db'
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
    
    conn.close()
    print("\n✅ Database check complete!")
except Exception as e:
    print(f"❌ Error: {e}")

