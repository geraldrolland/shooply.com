from random import choice
def generate_model_id(prefix, iteration_count=8):
    char = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', 
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'l',
        'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
        ]
    
    string = ""
    for i in range(0, iteration_count):
        string += choice(char)
    return f'{prefix}_{string}'
