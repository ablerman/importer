import random

integer_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']


def generate_ssn():
    ssn = ''.join(random.choices(integer_list, k=3))
    ssn += '-'
    ssn += ''.join(random.choices(integer_list, k=2))
    ssn += '-'
    ssn += ''.join(random.choices(integer_list, k=4))
    return ssn

