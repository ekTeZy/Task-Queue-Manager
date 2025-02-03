import re

def validate_name(name):
    return re.sub(r"[^a-zA-Z0-9 _-]", "", name) 

def user_data_validation(**user_data):
    for key in user_data:
        value = user_data.get(key)

        if key == 'username':
            if len(value) < 4:
                raise Exception("Username must be at least 4 characters long.")
            if not re.match(r'^[A-Za-z0-9]+$', value):
                raise Exception("Username can only contain letters and numbers.")

        if key == "password":
            if not 6 <= len(value) <= 12:
                raise Exception("The password must be between 6 and 12 characters long.")

            if not re.search(r'[A-Z]', value):
                raise Exception("Password must contain at least one uppercase letter.")

            if not re.search(r'[a-z]', value):
                raise Exception("Password must contain at least one lowercase letter.")

            if not re.search(r'[0-9]', value):
                raise Exception("Password must contain at least one digit.")

            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
                raise Exception("Password must contain at least one special character.")
