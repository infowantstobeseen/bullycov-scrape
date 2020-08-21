"""bullycov-scrape.py

Connects to the Mississippi State Universtiy Latest COVID testing site and
scrapes the latest week's positive cases. Web page at:
    https://www.msstate.edu/covid19/campus-testing
"""
import json
from pathlib import Path

# Scrapping code adapted from the very helpful 
#   https://docs.python-guide.org/scenarios/scrape/
from lxml import html
import requests

# Constants

site = 'https://www.msstate.edu/covid19/campus-testing'
update_path = '//*[@id="block-msstate-theme-content"]/article/div/div/p[1]/em/text()'
employees_pos_path = '//table[2]//tr[1]/td[1]/text()'
students_pos_path  = '//table[2]//tr[3]/td[1]/text()'
employees_neg_path = '//table[2]//tr[1]/td[2]/text()'
students_neg_path  = '//table[2]//tr[3]/td[2]/text()'
num_employees = 4717  # Estimate from Wikipedia of Academic/Admin staff
num_students = 22587  # Official Fall 2020 est (include Distance at well)
json_file = Path("bullycov.json")

months = ["january", "february", "march", "april", "may", "june", "july", 
          "august", "september", "october", "november", "december"]

def to_int(s):
    if s == '' or s == u"\xa0":
        return 0
    else:
        return int(s)


def scrape():
    # Load page and parse
    page = requests.get(site)
    tree = html.fromstring(page.content)

    # Extract last update, put into iso-format for keying
    month, day, year = tree.xpath(update_path)[0].strip().replace(",", "").split()[-3:]
    month = months.index(month.lower()) + 1
    month, day = [int(x) for x in [month, day]]
    isodate = f"{year}{day:02}{month:02}"
    employees_positive = to_int(tree.xpath(employees_pos_path)[0])
    students_positive = to_int(tree.xpath(students_pos_path)[0])
    employees_negative = to_int(tree.xpath(employees_neg_path)[0])
    students_negative = to_int(tree.xpath(students_neg_path)[0])

    # Read old JSON file
    if json_file.exists():
        with json_file.open("r") as store:
            data = json.load(store)
    else: 
        data = []

    # Append if date not there already
    if not any(datum["date"] == isodate for datum in data):
        data.append({"date": isodate, 
                    "employees_positive": employees_positive, 
                    "employees_negative": employees_negative,
                    "students_positive": students_positive,
                    "students_negative": students_negative})

        # Update JSON
        with json_file.open("w") as store:
            json.dump(data, store, indent=2)


if __name__ == "__main__":
    scrape()

