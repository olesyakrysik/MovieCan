import random
import re
from os import listdir

import lxml.html


def word_declension(number, variants):
    variants = variants.split(",")
    value = abs(int(number))

    if value % 10 == 1 and value % 100 != 11:
        variant = 0
    elif value % 10 >= 2 and value % 10 <= 4 and \
            (value % 100 < 10 or value % 100 >= 20):
        variant = 1
    else:
        variant = 2

    return variants[variant]


def generate_name(dir_path):
    string = ''
    list_word = *range(65, 90), *range(48, 57)

    names = [i.split(".")[0] if "." in i else "" for i in listdir(dir_path)]

    for i in range(25):
        string += chr(random.choice(list_word))

    if string in names:
        string = generate_name(dir_path)

    return string.strip()

def find_link_in_text(text):
    modify_text = text

    urls_http = re.findall(r'http://\S+', modify_text)
    urls_https = re.findall(r'https://\S+', modify_text)

    for url in urls_http:
        modify_text = modify_text.replace(url, f"<a href={url} style='text-decoration: none; color: rgba(6,95,212,1.000);'>{url}</a>")

    for url in urls_https:
        modify_text = modify_text.replace(url, f"<a href={url} style='text-decoration: none; color: rgba(6,95,212,1.000);'>{url}</a>")

    return modify_text