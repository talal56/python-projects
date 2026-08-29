alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

text = input("Enter encrypted text: ")
key = int(input("Enter key: "))

decrypted = ""

for letter in text:
    if letter.upper() in alphabet:
        is_lower = letter.islower()
        position = alphabet.index(letter.upper())
        new_position = (position - key) % 26
        new_letter = alphabet[new_position]
        decrypted += new_letter.lower() if is_lower else new_letter
    else:
        decrypted += letter  # keep spaces, punctuation, digits unchanged

print("Decrypted:", decrypted)