alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

text = input("Enter text: ")
key = int(input("Enter key: "))

encrypted = ""

for letter in text:
    if letter.upper() in alphabet:
        is_lower = letter.islower()
        position = alphabet.index(letter.upper())
        new_position = (position + key) % 26
        new_letter = alphabet[new_position]
        encrypted += new_letter.lower() if is_lower else new_letter
    else:
        encrypted += letter  # keep spaces, punctuation, digits unchanged

print("Encrypted:", encrypted)