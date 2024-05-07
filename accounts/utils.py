from secrets import SystemRandom, choice
from string import ascii_lowercase, ascii_uppercase, digits


def generate_strong_password(length: int = 12) -> str:
    """
    Generate a strong password with specified length.

    Parameters:
        length (int): The length of the password to be generated. Default is 12.

    Returns:
        str: A strong password containing at least one lowercase letter,
             one uppercase letter, one digit, and one special character.

    Notes:
        This function uses the secrets module to generate a strong password
        with sufficient randomness. The generated password will contain at
        least one character from each of the following character sets:
        - Lowercase letters (a-z)
        - Uppercase letters (A-Z)
        - Digits (0-9)
        - Special characters (such as !@#$%^&*)

        The remaining characters in the password are randomly chosen from
        all character sets. The final password is shuffled to ensure randomness.
    """

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
