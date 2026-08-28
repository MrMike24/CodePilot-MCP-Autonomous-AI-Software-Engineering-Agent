def create_user(user):
    if not user.email or not user.email.strip():
        raise HTTPException(status_code=400, detail="Email cannot be empty")
