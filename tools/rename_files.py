import os
import re

DIRECTORY = "./server/static/assets/temp"
PATTERN = re.compile(r'__orange_angelfish_swim_(\d{3})')
NEW_PREFIX = "idle_"

def rename_files(directory):

    for filename in os.listdir(directory):
        match = PATTERN.match(filename)
        if match:
            new_filename = f'{NEW_PREFIX}{match.group(1)}'
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, new_filename + ".png")
            os.rename(old_file, new_file)
            print(f'Renamed: {old_file} to {new_file}')

rename_files(DIRECTORY)