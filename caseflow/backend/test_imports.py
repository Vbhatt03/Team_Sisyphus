try:
    from models import User, Case
    print("Models OK")
except Exception as e:
    print(f"Models error: {e}")

try:
    from auth import verify_password
    print("Auth OK")
except Exception as e:
    print(f"Auth error: {e}")

try:
    from processors import DocumentProcessor
    print("Processors OK")
except Exception as e:
    print(f"Processors error: {e}")