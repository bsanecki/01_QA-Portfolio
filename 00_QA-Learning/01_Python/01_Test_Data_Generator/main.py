from function_base import TestDataGenerator, menu
import json
import time


generator = TestDataGenerator()


try:
    with open("database.json", "r", encoding="utf-8") as file:
        generator.users = json.load(file)

except (FileNotFoundError, json.JSONDecodeError):
    generator.users = []




while True:

    menu_page = menu()

    if menu_page == '1':

        generator.generator_id()
        generator.username_generator()
        generator.password_generator()
        generator.phone_number_generator()
        generator.birth_date_generator()
        generator.email_generator()

        user = {
            "id": generator.user_id,
            "username": generator.username,
            "password": generator.password,
            "phone": generator.phone_number,
            "age": generator.user_age,
            "birth_date": generator.born_date,
            "email": generator.user_email
        }

        generator.users.append(user)

        with open("database.json", "w", encoding="utf-8") as file:
            json.dump(generator.users, file, indent=4, ensure_ascii=False)

        print("\nUser generated successfully!")
        time.sleep(2)


    elif menu_page == '2':

        try:
            amount = int(input("\nHow many users do you want to generate? "))

            if amount <= 0:
                print("\nAmount must be greater than 0.")
                time.sleep(2)
                continue

            for _ in range(amount):

                generator.generator_id()
                generator.username_generator()
                generator.password_generator()
                generator.phone_number_generator()
                generator.birth_date_generator()
                generator.email_generator()

                user = {
                    "id": generator.user_id,
                    "username": generator.username,
                    "password": generator.password,
                    "phone": generator.phone_number,
                    "age": generator.user_age,
                    "birth_date": generator.born_date,
                    "email": generator.user_email
                }

                generator.users.append(user)

            with open("database.json", "w", encoding="utf-8") as file:
                json.dump(generator.users, file, indent=4, ensure_ascii=False)

            print(f"\nSuccessfully generated {amount} users!")
            time.sleep(2)

        except ValueError:
            print("\nPlease enter a valid number.")
            time.sleep(2)


    elif menu_page == '3':

        try:
            user_id = int(input("\nEnter user ID: "))

            found_user = None

            for user in generator.users:
                if user["id"] == user_id:
                    found_user = user
                    break

            if found_user:
                print("\n========================================")
                print("              USER FOUND")
                print("========================================")
                print(f"ID:          {found_user['id']}")
                print(f"Username:    {found_user['username']}")
                print(f"Password:    {found_user['password']}")
                print(f"Phone:       {found_user['phone']}")
                print(f"Age:         {found_user['age']}")
                print(f"Birth date:  {found_user['birth_date']}")
                print(f"Email:       {found_user['email']}")
                print("========================================")
            else:
                print("\nUser with this ID was not found.")

            time.sleep(4)

        except ValueError:
            print("\nPlease enter a valid ID.")
            time.sleep(2)


    elif menu_page == '4':

        if not generator.users:
            print("\nNo users generated yet.")
            time.sleep(2)
            continue

        print("\n========================================")
        print("              ALL USERS")
        print("========================================")

        for user in generator.users:
            print(f"""
ID:          {user['id']}
Username:    {user['username']}
Password:    {user['password']}
Phone:       {user['phone']}
Age:         {user['age']}
Birth date:  {user['birth_date']}
Email:       {user['email']}
----------------------------------------
""")

        input("Press Enter to continue...")


    elif menu_page == '0':
        print("\nGoodbye!")
        time.sleep(1)
        break