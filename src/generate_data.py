#!/usr/bin/env python 
import csv
import random
import math
from factories import generate_ssn, generate_last_name, generate_first_name


def add_member(data):
    data.append({
        'ssn': generate_ssn(),
        'first_name': generate_first_name(),
        'last_name': generate_last_name(),
    })
    return data


def remove_member(data):
    index = random.randrange(0, len(data))
    del data[index]
    return data


def create_generation(previous_generation):
    new_set = previous_generation[:]
    min_changes = math.floor(len(previous_generation)*0.6)
    max_changes = math.floor(len(previous_generation)*0.9)
    change_count = random.randrange(min_changes, max_changes)
    change_functions = [add_member, remove_member]
    for i in range(change_count):
        new_set = random.choice(change_functions)(new_set)

    print(f'{len(previous_generation)}: {len(new_set)}')
    return new_set


def create_prime(member_count=100):
    member_list = []
    for m in range(member_count):
        member_list.append({
            'ssn': generate_ssn(),
            'first_name': generate_first_name(),
            'last_name': generate_last_name(),
        })
    return member_list


def write_data(data, dest_path):
    with open(dest_path, 'w') as f:
        writer = csv.DictWriter(f, data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def main():
    dest_path = './data/sample1/'
    generations = 10
    data = list()
    data.append(create_prime(10000))

    for i in range(1, generations):
        data.append(create_generation(data[i-1]))

    for index, d in enumerate(data):
        write_data(d, f'{dest_path}{index}.csv')


if __name__ == '__main__':
    main()
