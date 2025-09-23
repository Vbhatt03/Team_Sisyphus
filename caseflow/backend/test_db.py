from models import create_db_and_tables
try:
    create_db_and_tables()
    print('Tables created successfully')
except Exception as e:
    print(f'Database error: {e}')
    import traceback
    traceback.print_exc()