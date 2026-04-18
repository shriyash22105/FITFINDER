import os
from sqlalchemy import create_engine, inspect, text

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+psycopg://postgres:postgres@localhost:5432/fitfinder')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
elif DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("=== FitFinder Database Tables ===")
    print("Database URL:", DATABASE_URL)
    print("Tables:", ', '.join(tables) if tables else '(none)')
    print()

    main_tables = ['users', 'user_profiles', 'saved_outfits', 'try_on_history', 'outfits', 'contact_messages']
    print("=== Entry Counts ===")
    with engine.connect() as conn:
        for table in main_tables:
            if table in tables:
                count = conn.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
                print(f"{table}: {count}")
            else:
                print(f"{table}: 0 (table missing)")

        print("\n=== Sample Users (top 3) ===")
        if 'users' in tables:
            users = conn.execute(text('SELECT id, userid, role FROM users LIMIT 3')).fetchall()
            if users:
                for user in users:
                    print(f"  ID:{user[0]} {user[1]} ({user[2]})")
            else:
                print("  No users found")
        else:
            print("  users table missing")

    print("\n✅ PostgreSQL database check complete!")
except Exception as e:
    print(f"❌ Error: {e}")

