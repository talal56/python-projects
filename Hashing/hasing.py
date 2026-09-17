import hashlib
message = input("Enter Your Message :")
hashedValue = hashlib.sha256(message.encode()).hexdigest()
print("Message : ", message)
print("Hashed Value : ", hashedValue)