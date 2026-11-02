import random
import string
from datetime import date,timedelta

class TestDataGenerator:

    words = [
        "adam", "anna", "jan", "maria", "piotr",
        "kamil", "tomasz", "kasia", "pawel", "ola",
        "mateusz", "natalia", "michal", "karolina", "jakub",
        "aleksandra", "marcin", "monika", "szymon", "weronika",

        "cat", "dog", "wolf", "fox", "bear",
        "lion", "tiger", "eagle", "hawk", "rabbit",
        "horse", "mouse", "panda", "turtle", "shark",
        "owl", "deer", "otter", "penguin", "snake",

        "computer", "phone", "keyboard", "mouse", "camera",
        "book", "lamp", "chair", "table", "clock",
        "bottle", "backpack", "guitar", "pencil", "notebook",
        "helmet", "wallet", "watch", "key", "umbrella",

        "city", "forest", "mountain", "river", "island",
        "desert", "castle", "village", "beach", "garden",
        "lake", "valley", "bridge", "station", "park",

        "red", "blue", "green", "black", "white",
        "yellow", "purple", "orange", "pink", "brown",
        "silver", "gold", "gray", "violet", "cyan"
    ]

    email_domains = [
    "example.com",
    "example.net",
    "test.com",
    "mail.test",
    "qa.test"
    
    ]



    def __init__(self):
        self.user_id = None
        self.username = None
        self.password = None
        self.phone_number = None
        self.user_age = None
        self.born_date = None
        self.user_email = None
        self.users = []

        

    def generator_id(self):
        self.user_id = len(self.users) + 1
        return self.user_id

    def username_generator(self):
        first = random.choice(self.words)
        second = random.choice(self.words)
        number = random.randint(0, 1000)
        number = str(number)

        self.username = first + "_" + second + number

        return self.username

    def password_generator(self):
        number = random.randint(16, 33)

        password_signs = []

        Signs = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation

        count = 0

        while count != number:
            sign = random.choice(Signs)
            count += 1
            password_signs.append(sign)

        self.password = "".join(password_signs)

        return self.password

    def phone_number_generator(self):
        self.phone_number = random.randint(100_000_000, 999_999_999)

        return self.phone_number


    def birth_date_generator(self):
        today_date = date.today()
        self.user_age = random.randint(16,94)
        days_from_born = timedelta(days = self.user_age * 365)
        self.born_date = today_date - days_from_born
        self.born_date = self.born_date.strftime('%d.%m.%Y')
        return self.user_age,self.born_date


    def email_generator(self):
        self.user_email = self.username + "@" + random.choice(self.email_domains)
        return self.user_email


def menu():
    print("""
========================================
          TEST DATA GENERATOR
========================================

[1] Generate one user
[2] Generate multiple users
[3] Find user by ID
[4] Show all users
[0] Exit

========================================
""")

    choice = input("Choose an option: ")

    return choice





