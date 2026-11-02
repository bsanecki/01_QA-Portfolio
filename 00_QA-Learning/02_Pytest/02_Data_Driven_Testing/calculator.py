def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def calculate_discount(price, discount):
    if price < 0:
        raise ValueError("Price cannot be negative.")

    if discount < 0 or discount > 100:
        raise ValueError("Discount must be between 0 and 100.")

    return price - (price * discount / 100)


def calculate_tax(price, tax_rate):
    if price < 0:
        raise ValueError("Price cannot be negative.")

    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative.")

    return price + (price * tax_rate / 100)


def calculate_final_price(price, discount, tax_rate):
    discounted_price = calculate_discount(price, discount)
    final_price = calculate_tax(discounted_price, tax_rate)

    return final_price


def main():
    print("=== Python Calculator ===")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")
    print("5. Calculate discount")
    print("6. Calculate final price with discount and tax")

    choice = input("Choose an operation: ")

    try:
        if choice in ["1", "2", "3", "4"]:
            first_number = float(input("Enter first number: "))
            second_number = float(input("Enter second number: "))

            if choice == "1":
                result = add(first_number, second_number)

            elif choice == "2":
                result = subtract(first_number, second_number)

            elif choice == "3":
                result = multiply(first_number, second_number)

            else:
                result = divide(first_number, second_number)

            print(f"Result: {result:.2f}")

        elif choice == "5":
            price = float(input("Enter product price: "))
            discount = float(input("Enter discount (%): "))

            result = calculate_discount(price, discount)

            print(f"Price after discount: {result:.2f}")

        elif choice == "6":
            price = float(input("Enter product price: "))
            discount = float(input("Enter discount (%): "))
            tax_rate = float(input("Enter tax rate (%): "))

            result = calculate_final_price(
                price,
                discount,
                tax_rate
            )

            print(f"Final price: {result:.2f}")

        else:
            print("Invalid operation.")

    except ValueError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()