#! python3
import math
import PIL
from PIL import Image
import os
import re
import argparse
import csv
import re
import logging
logging.basicConfig(filename='othfilter.log',
                    filemode='a',
                    level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())
logging.info('starting othFilter....')



def filter_words(product_name):
    for word in filtered_words:
        if product_name.__contains__(word):
            global counter
            counter += 1
            print('row removed: \n {}'.format(product_name))
            return False
    return True


def get_csv_files(root='.'):
    for dirpath, dirnames, files in os.walk(root):
        for filename in files:
            if filename.split('.')[-1] == 'csv':
                yield os.path.join(dirpath, filename)


def get_pictures_path(root='.'):
    for dirpath, dirnames, files in os.walk(root):
        for filename in files:
            if filename.split('.')[-1] == 'jpg':
                yield os.path.join(dirpath, filename)


def remove_picture(path, name):
    filename = '{}.jpg'.format(name)
    path = os.path.join(*path, filename)
    try:
        os.remove(path)
    except:
        print('{} DOES NOT EXIST'.format(path))


def remove_unwanted_products(csv_files):
    for filename in csv_files:
        new_csv_list = []
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if filter_words(row[2]):
                    new_csv_list.append(row)
                else:
                    remove_picture(filename.split('/')[:4], row[0])
        with open(filename, 'w+') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(new_csv_list)


def correct_prices(csv_files):
    for filename in csv_files:
        new_rows = []
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                print(row[3])
                try:
                    if re.match(r'^[0-9]*.95', row[3]) is not None:
                        print('hihi')
                        row[3] = math.ceil(float(row[3]))
                        new_rows.append(row)
                    else:
                        new_rows.append(row)

                except:
                    pass
        with open(filename, 'w+') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(new_rows)


def redcuce_image_size():

    text_file = open('no_pictures.txt', 'w+')
    for picture_path in get_pictures_path():
        try:
            picture = Image.open(picture_path)
            print(picture.size)
            picture = picture.resize((170, 165), Image.ANTIALIAS)
            picture.save(picture_path, optimize=True, quality=85)
            picture = Image.open(picture_path)
            print(picture.size)
        except Exception as error:
            text_file.write('{}\n'.format(picture_path))
            logging.error(error)
            logging.info(picture_path)


filtered_words = open('filter.txt', 'r').read().strip().split('\n')
counter = 0


def main():
    print(PIL.PILLOW_VERSION)

    csv_files = []
    for filename in get_csv_files():
        csv_files.append(filename)

    # remove_unwanted_products(csv_files)
    print('counter = ', counter)
    # redcuce_image_size()
    # correct_prices(csv_files)
    remove_unwanted_products(csv_files)


main()
