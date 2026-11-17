#!/usr/bin/env python3
# Load raw_data/states.csv into Python structures.


import csv
import os


def load_states(file_path):
    """
    Load states from a CSV file and return a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.
    """
    states = []
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            states.append(row)
    return states


def load_state_coordinates(file_path):
    """
    Return a map of state abbreviation to latitude and longitude floats.

    CSV columns: Abbrev, Latitude, Longitude, State.
    """
    coords = {}
    for row in load_states(file_path):
        abbrev = row['Abbrev']
        coords[abbrev] = {
            'latitude': float(row['Latitude']),
            'longitude': float(row['Longitude']),
        }
    return coords


def main():
    # accept the file path as an argumen
    if len(os.sys.argv) > 1:
        file_path = os.sys.argv[1]
    else:
        print("USAGE: python load.py <path_to_states_csv>")
        exit(1)

    # Load states from the CSV file
    states = load_states(file_path)

    # Print the loaded states
    for state in states:
        print(state)


if __name__ == "__main__":
    main()
