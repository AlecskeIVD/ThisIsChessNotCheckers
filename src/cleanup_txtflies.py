import os
import re


def remove_metadata(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        # Use regular expression to remove metadata in brackets
        cleaned_content = re.sub(r'\[.*?]\n', '', content)
        cleaned_content = re.sub(r'\+', '', cleaned_content)

    with open(file_path, 'w') as file:
        file.write(cleaned_content)


def main():
    path = '/Users/alecvandeuren/ThisIsChessNotCheckers/assets/GM_games/WijkaanZee'
    for year in range(2006, 2021):
        temp_path = path + str(year) + '.txt'
        print(temp_path)
        remove_metadata(temp_path)


if __name__ == '__main__':
    main()