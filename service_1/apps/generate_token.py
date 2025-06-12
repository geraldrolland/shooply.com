from random import choice


def generate_token():
    token = ""
    for i in range(0, 17):
        token += choice(["@", "#", "$", "%", "^", ")", "(", "&", "*", "-", "+", "!", "/", "<", ">"])
    return token