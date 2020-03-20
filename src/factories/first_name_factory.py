import os
import csv
import random

path = os.path.dirname(os.path.realpath(__file__))
f = open(f'{path}/first_names.csv')
csv_reader = csv.reader(f)
first_names = []
# for index, row in enumerate(csv_reader):
#     print(index, ' ', f)
#     first_names.append(row[1])
first_names = [row[1].lower().capitalize() for row in csv_reader]


def generate_first_name():
    return random.choice(first_names)
