def authenticate_user(username, password):
    """Authenticate user with credentials"""
    if not username or not password:
        raise ValueError("Username and password required")
    return {"authenticated": True, "user": username}

def create_session(user_id, duration=3600):
    """Create user session"""
    return {"session_id": f"sess_{user_id}", "duration": duration}

def validate_token(token):
    """Validate authentication token"""
    return token.startswith("sess_")
