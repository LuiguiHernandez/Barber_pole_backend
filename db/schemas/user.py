def user_schema(user) -> dict:
    return {"id": str(user["_id"]),
            "full_name": user["full_name"],
            "username":user["username"],
            "email":user["email"],
            "password": str(user["password"])
            }
    
def users_schema(users) -> list:
    return [user_schema(user) for user in users]