from collections import Counter
import numpy as np
import pickle
import re
from sys import argv, exit

## GLOBAL VARIABLES ##
customers = {} # key: Id, value: {ASIN: [rating, votes, helpful]} of products purchased 
products = {} 	# key: ASIN, value: {title (string), group (string), categories (set of category Ids), reviews (list of customer Ids)}

## REGEX ##
REGEX_TOTAL = re.compile(r"total: (\d+)")
REGEX_REVIEW = re.compile(r"cutomer:\s*(\w+)*\s*rating:\s*(\d+)\s*votes:\s*(\d+).*helpful:\s*(\d+)")

def find_category_n_digits(all_cats, n):
    s = set()
    for i in all_cats:
        if len(str(i)) == n:
            s.add(i)
    return s

def parse_lines(lines, n):
    global customers, products

    i = 3
    while i < n:
        # Id
        split = lines[i].split(':')
        Id = split[1].strip()
        i += 1

        # ASIN
        split = lines[i].split(':')
        ASIN = split[1].strip()
        i += 1

        if lines[i].strip() == "discontinued product":
            i += 2
            continue

        # Title
        split = lines[i].partition(':')
        title = split[2].strip()
        i += 1

        # Group
        split = lines[i].split(':')
        group = split[1].strip()
        i += 3 # skip salesrank and similar for now

        # categories
        split = lines[i].partition(':')
        n_cats = int(split[2].strip())
        cats = set()
        pattern = re.compile(r"\d+")
        for j in range(n_cats):
            i += 1
            all_cats = pattern.findall(lines[i])
            if group == "Book" and '1000' in all_cats:
                cats = cats | find_category_n_digits(all_cats, 1)
                cats = cats | find_category_n_digits(all_cats, 2)
            elif group == "Music" and '301668' in all_cats:
                cats = cats | find_category_n_digits(all_cats, 1)
                cats = cats | find_category_n_digits(all_cats, 2)
                pass
            elif group == "Video" and '404274' in all_cats:
                cats = cats | find_category_n_digits(all_cats, 3)
            elif group == "DVD" and '404276' in all_cats:
                ind = all_cats.index('404276')
                cats = cats | {all_cats[ind+1]}
        i += 1

        # Add product info
        products[ASIN] = {'title': title, 'group': group, 'categories': cats, 'reviews': set()}

        # reviews
        pattern = REGEX_TOTAL
        n_reviews = int(pattern.search(lines[i]).group(1))
        i += 1
        while lines[i].strip() != "":
            pattern = REGEX_REVIEW
            s = pattern.search(lines[i])
            customer_Id = s.group(1)

            rating = int(s.group(2))
            votes = int(s.group(3))
            helpful = int(s.group(4))

            products[ASIN]['reviews'].add(customer_Id)
            if customer_Id not in customers:
                customers[customer_Id] = {}
            customers[customer_Id][ASIN] = [rating, votes, helpful]

            i += 1

        # next product
        i += 1

# Read data from infile
def read_infile(infile):
    data = []
    with open(infile) as f:
        # skip first 3 lines
        lines = f.readlines()
        # parse file
        parse_lines(lines, len(lines))

def write_pickle_files():
    global customers, products

    p = open("products.pkl", "wb")
    pickle.dump(products, p)
    p.close()

    c = open("customers.pkl", "wb")
    pickle.dump(customers, c)
    c.close()

def main():
    if len(argv) != 2:
        raise Exception("usage: python extract_data.py <infile>")

    infile = argv[1]
    read_infile(infile)
    write_pickle_files()

if __name__ == '__main__':
    main()