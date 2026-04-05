import hashlib


def save_creds(path, username, password):
    import hashlib
    hash_pass = hashlib.sha256(password.encode()).hexdigest()

    with open(path, "w") as f:
        f.write(username + "\n")
        f.write(hash_pass + "\n")


save_creds("./creds.txt", "admin", "yeoldpass")
