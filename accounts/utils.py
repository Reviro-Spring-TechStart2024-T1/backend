from secrets import SystemRandom, choice
from string import ascii_lowercase, ascii_uppercase, digits


def generate_strong_password(length=12):
    # Define character sets
    lowercase_letters = ascii_lowercase
    uppercase_letters = ascii_uppercase
    special_characters = '!@#$%^&*'

    # Ensure at least one character from each character set
    password = (
        choice(lowercase_letters) +  # noqa: W504
        choice(uppercase_letters) +  # noqa: W504
        choice(digits) +  # noqa: W504
        choice(special_characters)
    )

    # Generate the rest of the password
    password += ''.join(choice(lowercase_letters + uppercase_letters + digits + special_characters)
                        for _ in range(length - 4))

    # Shuffle the password to ensure randomness
    password_list = list(password)
    SystemRandom().shuffle(password_list)
    password = ''.join(password_list)

    return password
