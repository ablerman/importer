#!/usr/bin/env python 
from os import listdir
from os.path import isfile, join
import csv
from datetime import datetime
import json
from db import engine
from sqlalchemy.sql import text
import time


def create_events(census_id):
    with engine.begin() as conn:
        create_events_query = text('''
            INSERT INTO event(event_type_id, census_id, unique_key, data)
            SELECT   
                (SELECT id FROM event_type WHERE name = 'CREATE_MEMBER'),
                :census_id,
                raw_member.unique_key,
                raw_member.data
            FROM raw_member
            LEFT OUTER JOIN member ON raw_member.unique_key = member.unique_key
            WHERE member.id IS NULL
            AND raw_member.census_id = :census_id
            ;        
        ''')
        result = conn.execute(create_events_query, census_id=census_id)

        deactivate_events_query = text('''
            INSERT INTO event(event_type_id, census_id, unique_key)
            SELECT
                (SELECT id FROM event_type WHERE name = 'DEACTIVATE_MEMBER'),
                :census_id,
                member.unique_key                           
            FROM member
            LEFT OUTER JOIN raw_member ON raw_member.unique_key = member.unique_key AND raw_member.census_id = :census_id
            WHERE 1=1
                AND raw_member.id IS NULL        
        ''')
        result = conn.execute(deactivate_events_query, census_id=census_id)


def apply_events(census_id):
    create_event_id = 1
    deactivate_event_id = 2
    with engine.begin() as conn:
        apply_create_events_query = text('''
            INSERT INTO member(unique_key, deactivated_at, first_name, last_name, ssn)
            SELECT
                (event.data->>'first_name')::text || (event.data->>'last_name')::text || (event.data->>'ssn')::text,
                null,
                (event.data->>'first_name')::text,
                (event.data->>'last_name')::text,
                (event.data->>'ssn')::text
            FROM event
            WHERE event.census_id = :census_id
            AND event.event_type_id = :create_event_id
            AND event.applied_at IS NULL
        ''')
        result = conn.execute(apply_create_events_query, census_id=census_id, create_event_id=create_event_id)
        mark_events_applied_query = text('''
            UPDATE event 
            SET applied_at = now()
            WHERE census_id = :census_id
            AND event_type_id = :create_event_id
        ''')
        result = conn.execute(mark_events_applied_query, census_id=census_id, create_event_id=create_event_id)

        apply_deactivate_events_query = text('''
            UPDATE member
            SET deactivated_at = now()
            FROM event
            WHERE event.event_type_id = :deactivate_event_id
            AND member.unique_key = event.unique_key
            AND census_id = :census_id
        ''')
        result = conn.execute(apply_deactivate_events_query, census_id=census_id, deactivate_event_id=deactivate_event_id)
        mark_events_applied_query = text('''
            UPDATE event
            SET applied_at = now()
            WHERE census_id = :census_id
            AND event_type_id = :deactivate_event_id
        ''')
        result = conn.execute(mark_events_applied_query, census_id=census_id, deactivate_event_id=deactivate_event_id)


def import_census(path):
    with engine.begin() as conn:
        insert_query = text('''
            INSERT INTO census(path, created_at)
            VALUES(:path, :now)
            ON CONFLICT(path) DO UPDATE SET path=EXCLUDED.path
            RETURNING id
        ''')
        result = conn.execute(insert_query, path=path, now=datetime.now()).fetchall()
        census_id = result[0][0]

        # go through the data and insert it all as raw values
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                insert_value_query = text('''
                    INSERT INTO raw_member(census_id, unique_key, data) 
                    VALUES(:census_id, :key, :data)
                    ON CONFLICT DO NOTHING
                ''')
                key = f"{row['first_name']}{row['last_name']}{row['ssn']}"
                conn.execute(insert_value_query, census_id=census_id, key=key, data=json.dumps(row))
        return census_id


def main():
    path = './data/sample1'
    filenames = [f for f in listdir(path) if isfile(f'{path}/{f}')]
    filenames = sorted(filenames)
    for f in filenames:
        start = time.time()
        print(f'Importing census {f}')

        census_id = import_census(f'{path}/{f}')
        create_events(census_id)
        apply_events(census_id)
        print(f'\tcensus imported in {time.time() - start} seconds')


if __name__ == '__main__':
    main()
