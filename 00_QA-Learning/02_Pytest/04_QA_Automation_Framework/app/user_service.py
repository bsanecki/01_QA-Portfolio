class UserService:
    def __init__(self, user_api):
        self.user_api = user_api

    def get_user(self, user_id):
        user = self.user_api.get_user(user_id)

        if user is None:
            raise LookupError("User not found.")

        return user

    def get_user_name(self, user_id):
        user = self.get_user(user_id)
        return user["name"]

    def is_active(self, user_id):
        user = self.get_user(user_id)
        return user["status"] == "active"

    def create_user(self, name, email):
        if not name.strip():
            raise ValueError("Name cannot be empty.")

        if "@" not in email:
            raise ValueError("Invalid email.")

        return self.user_api.create_user({
            "name": name,
            "email": email,
            "status": "active",
        })
