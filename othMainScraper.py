#! python3

import threading
import re
import shutil
import bs4
import os
import csv
import logging
import requests

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.3ci6'
COOKIE = 'frontend=4fc2a2f665ab20702f316fad0efa83c1; __utma=64338161.12960362.1522093959.1522093959.1522093959.1; __utmb=64338161.11.10.1522093959; __utmc=64338161; __utmz=64338161.1522093959.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); cookie_country=sa; __ar_v4=QEZYSDRFGVA5PHP46IA43E%3A20180325%3A4%7CMOUPUUQ7V5ETTP5ZPQDOAT%3A20180325%3A4%7CBPHNGPC7FNDD3CBVQ6LP6Q%3A20180325%3A4'
ACCEPT_LANGUAGE = "Accept-Language: en-US,en;q=0.9,en-SA;q=0.8,en;q=0.7"
HEADERS = {'User-Agent': USER_AGENT,
           'Cookie': COOKIE,
           'Accept_Language': ACCEPT_LANGUAGE}
language_en = "___from_store=ar&___store=en"
language_ar = "___from_store=ar&___store=ar"
URL = 'will get overridden'
product_csv = ''
URLS_PATH = 'urls.txt'


def replace_img_small_to_big(url):
    # AD SPOTTED! not a product image
    if url.find('50x48') != -1:
        return 'AD'
    url = url.replace('small_image', 'image')
    url = url.replace('170x165', '720x680')
    return url


def remove_invalid_chars(filename):
    filename = re.sub('-', '_', filename)
    filename = re.sub((r'[/\\"*\-+|*?:<>]'), '', filename)
    if filename == '':
        return 'null'
    return filename


def get_parsed_product_info(language=language_ar, page_num=1,
                            get_catagories=False):
    url = '{0}?{1}&p={2}'.format(URL, language, page_num)
    page = requests.get(url, headers=HEADERS).text
    content = bs4.BeautifulSoup(page, 'lxml')
    parsed_product_div = content.find_all(
        'div', attrs={'class': 'span2 product'})

    if get_catagories:
        catagory = content.title.string.split('-')[1].strip()
        sub_catagory = content.title.string.split('-')[0].strip()
        return catagory, sub_catagory
    return parsed_product_div


def get_product_info(parsed_element):
    image = parsed_element.find(
        'img', attrs={'class': 'product-retina'}).get('src')
    image_big = replace_img_small_to_big(image)
    if image_big == 'AD':
        return 'AD'

    price = parsed_element.find(
        'span', attrs={'class': 'price'}).get_text().strip()
    name = remove_invalid_chars(parsed_element.find(
        'img', attrs={'class': 'product-retina'}).get('alt'))
    return {'image': image_big, 'price': price, 'name': name}


def write_to_csv(path='null', product_csv='null', writer='null',
                 image_url='null', counter='null', name='null', name_en='no', price='null', catagory='null', subcatagory='null', catagory_en='null', subcatagory_en='null', init=False):
    if init:
        products_csv = open(path, 'w+', newline='',
                            encoding='utf-8')
        fieldnames = ['#', 'Name', 'Name_en', 'Price',
                      'Image_url', 'Catagory', 'Subcatagory', 'Catagory_en', 'Subcatagory_en']
        writer = csv.DictWriter(products_csv, fieldnames=fieldnames)
        writer.writeheader()
        return products_csv, writer
    else:
        writer.writerow({'#': counter, 'Name': name,
                         'Name_en': name_en, 'Price': price, 'Image_url': image_url,
                         'Catagory': catagory, 'Subcatagory': subcatagory, 'Catagory_en': catagory_en, 'Subcatagory_en': subcatagory_en})


def write_to_file(path, counter, image_url):
    image_url = requests.get(image_url, stream=True)
    try:
        with open('{0}//{1}.jpg'.format(path, counter), 'wb') as raw_image:
            shutil.copyfileobj(image_url.raw, raw_image)
    except OSError as error:
        logging.error(error)
        print('exception:', error)


def main():

    # read urls for catagoris from txt and put it an array
    urls = open(URLS_PATH, 'r').read().split('\n')

    counter = -1
    for url in urls:
        global URL
        URL = url
        exit = False
        # counter = -1
        first_product = 'save and compare 1st item each page (duplicates)'
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('URL = {}'.format(url))
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        catagory_name, subcatagory_name = get_parsed_product_info(
            get_catagories=True)
        catagory_name_en, subcatagory_name_en = get_parsed_product_info(
            get_catagories=True, language=language_en)
        
        print('Catagory = {} , Subcatagory = {}'.format(
            catagory_name, subcatagory_name))

        path = 'Products//{0}//{1}'.format(catagory_name_en,
                                           subcatagory_name_en)
        os.makedirs(path, exist_ok=True)
        product_csv, writer = write_to_csv(
            path='{0}//{1}.csv'.format(path, subcatagory_name_en), init=True)
        names_ar = []
        names_en = []
        prices = []
        counters = []
        image_urls = []

        for page_num in range(1, 30):

            products_info_ar = get_parsed_product_info(page_num=page_num)
            products_info_en = get_parsed_product_info(
                language=language_en, page_num=page_num)
            exit_counter = 0  # first product to catch duplicates
            print('-----------------------------------------')
            print('Page = {}'.format(page_num))
            print('-----------------------------------------')

            for element, element_en in zip(products_info_ar, products_info_en):
                exit_counter += 1
                product = get_product_info(element)
                product_en = get_product_info(element_en)
                if product == 'AD':
                    continue
                counter += 1
                if exit_counter == 1:
                    if product['name'] == first_product:
                        print('exiting duo to duplication.. next url...')
                        exit = True
                        break
                    first_product = product['name']
                print('Ar_Name:{0} \nPrice:{1}\nImage_url:{2}'.format(
                    product['name'], product['price'], product['image']))

                names_ar.append(product['name'])
                names_en.append(product_en['name'])
                if product_en['name'] == 'null':
                    names_en.remove(product_en['name'])
                prices.append(product['price'])
                image_urls.append(product['image'])
                counters.append(counter)

            if exit:
                break
        for i in range(len(names_en)):
            write_to_csv(writer=writer, name=names_ar[i],
                         price=prices[i], counter=counters[i],
                         name_en=names_en[i], image_url=image_urls[i],
                         catagory=catagory_name, subcatagory=subcatagory_name, catagory_en=catagory_name_en, subcatagory_en=subcatagory_name_en)
            thread = threading.Thread(target=write_to_file, name=counters[i],
                                      args=(path, counters[i], image_urls[i]))
            thread.start()
            # write_to_file(path, counters[i], image_urls[i])


main()
