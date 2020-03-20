import os
import csv
import random

path = os.path.dirname(os.path.realpath(__file__))
f = open(f'{path}/surnames.csv')

csv_reader = csv.reader(f)
first_names = [row[0].lower().capitalize() for row in csv_reader]


def generate_last_name():
    return random.choice(first_names)
