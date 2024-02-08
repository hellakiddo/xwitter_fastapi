def user(data) -> dict:
    return {
        "username":data["username"],
        "email":data["email"],
        "full_name": data["full_name"],

    }

def all_users(data) -> list:
    return [user(item) for item in data]