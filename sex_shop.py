import requests
import pymysql
import csv
from bs4 import BeautifulSoup
from pprint import pprint
from multiprocessing import Pool


ALL_DATA_DICT = dict()

def get_bs_object(url:str):
    try:
        html = requests.get(url).text
        bs_obj = BeautifulSoup(html, 'lxml')
    except:
        return None
    else:
        return bs_obj



# ================LINKS====================

def get_menu_links(bs_obj:BeautifulSoup):
    # PREPARATION
    try:
        menu_blocks_bs = bs_obj.find('td', {'class': 'left_menu'}).find_all('div', {'class': 'menu-block'})
    except:
        print('No find main-menu blocks')
        return None
    else:

    # WORK
        for block_bs in menu_blocks_bs:
            href_1 = _get_href_1(block_bs)
            if href_1 is not None:
                _deep_to_hrefs(href_1, block_bs)



def _get_href_1(block_bs: BeautifulSoup):
    try:
        href_1 = block_bs.find('div', {'class': 'menu-header'}).find('a', {'href': True}).get('href')
        if href_1 == '':
            href_1 = 'https://sex-shop.ua'
    except:
        return None
    else:
        return href_1


def _deep_to_hrefs(href_1: str, block_bs: BeautifulSoup):
    # PREPARATION
    try:
        li_all_bs = block_bs.find('ul', {'class': 'menu-body'}).find_all('li', recursive=False)
    except:
        print('No menu-body on ' + href_1)
        return
    else:

    # WORK
        href_2_dict = dict()
        for li_bs in li_all_bs:

            try:
                href_2 = li_bs.find('div').\
                               find('a', {'href': True}).\
                               get('href')

            except:
                continue

            else:
                href_3_bs = li_bs.find('div', {'class': 'menu-body hidden'})

                if href_3_bs is not None:
                    href_deep_dict = _get_href_3_dict_from(href_3_bs, href_2)
                    href_2_dict[href_2] = href_deep_dict

                else:
                    href_2_dict[href_2] = {href_2: list()}

        ALL_DATA_DICT[href_1] = href_2_dict


def _get_href_3_dict_from(href_3_bs: BeautifulSoup, href_2: str):
    href_3_dict = dict()
    all_li_bs = href_3_bs.find_all('li')

    if all_li_bs == 0:
        href_3_dict[href_2] = list()
        return href_3_dict

    for li_bs in all_li_bs:

        try:
            href_3 = li_bs.find('a', {'href': True}).get('href')
        except:
            continue
        else:
            href_3_dict[href_3] = list()

    return href_3_dict

"""RESULT: menu hrefs in ALL_DATA_DICT"""



# ==============POOL=====================

def start_pool_process():
    list_with_hrefs_tuples = _get_list_with_href_tuples()
    pool = Pool(40)
    print('===========START POOL===========')
    result = pool.map(get_from_one_page, list_with_hrefs_tuples)
    print('===========RESULT===========')
    _parse_result_from_pool(result)


def _get_list_with_href_tuples():

    list_with_href_tuples = list()

    for href_1, href_2_dict in ALL_DATA_DICT.items():

        for href_2, href_3_dict in href_2_dict.items():

            for href_3, l in href_3_dict.items():

                href_tuples = (href_1, href_2, href_3)
                list_with_href_tuples.append(href_tuples)

    return list_with_href_tuples


def _parse_result_from_pool(result: list):

    for dict_1 in result:
        if type(dict_1) is not dict:
            pprint(dict_1)
            continue

        for href_1, dict_2 in dict_1.items():
            if type(dict_2) is not dict:
                pprint(dict_2)
                continue

            for href_2, dict_3 in dict_2.items():
                if type(dict_3) is not dict:
                    pprint(dict_3)
                    continue

                for href_3, list_data in dict_3.items():
                    if type(list_data) is not list:
                        pprint(list_data)
                        continue

                    ALL_DATA_DICT[href_1][href_2][href_3] = list_data



# ==============DATA======================

def get_from_one_page(hrefs_tuple: tuple):

    try:
        href_1 = hrefs_tuple[0]
        href_2 = hrefs_tuple[1]
        href_3 = hrefs_tuple[2]
        url = 'https://sex-shop.ua' + href_3 + '?wp=1'
    except:
        return

    blocks_bs = _find_blocks_on_page(url)

    if blocks_bs is None:
        return

    list_data_page = list()

    for block_bs in blocks_bs:

        dic_data = _work_with_one_block(block_bs)
        list_data_page.append(dic_data)

    return {href_1: {href_2: {href_3: list_data_page}}}


def _find_blocks_on_page(url):
    bs_obj = get_bs_object(url)

    try:
        li_all_bs = bs_obj.find('div', {'id': 'gallery_cont'}). \
            find('ul', {'class': 'gallery'}). \
            find_all('li', recursive=False)

    except:
        print('No data-tags from  ' + url)
        return None

    else:
        return li_all_bs


def _work_with_one_block(block_bs: BeautifulSoup):
    dic = dict()
    dic['name'] = _get_name(block_bs)
    dic['href'] = _get_href(block_bs)
    pr_dict = _get_price(block_bs)
    dic['price'] = pr_dict['price']
    dic['old_price'] = pr_dict['old_price']
    dic['top'] = _get_top(block_bs)
    dic['available'] = _get_available(block_bs)
    return dic


# Data find
def _get_name(block_bs: BeautifulSoup):
    try:
        name = block_bs.find('div', {'class': 'gallery-item-name'}). \
            find('a', {'class': 'link fade in', 'data-original-title': True}). \
            get('data-original-title')
    except:
        print('Not find name')
        return None
    else:
        return name.strip()

def _get_href(block_bs: BeautifulSoup):
    try:
        href = block_bs.find('div', {'class': 'gallery-item-name'}). \
            find('a', {'class': 'link fade in', 'href': True}). \
            get('href')
    except:
        print('Not find href')
        return None
    else:
        return href

def _get_price(block_bs: BeautifulSoup):
    price_dict = {'price': None, 'old_price': None}

    try:
        price_block_bs = block_bs.find('div', {'class': 'gallery_info item_info'}). \
                                  find('span', {'class': 'price_highlited'})
    except:
        return price_dict
    else:
        price_bs = price_block_bs.find('b')
        old_price_bs = price_block_bs.find('span', {'class': 'sale_price'})

        price_str = None if price_bs is None else price_bs.text
        old_price_str = None if old_price_bs is None else old_price_bs.text

        price_dict['price'] = None if price_str is None else _clear_price(price_str)
        price_dict['old_price'] = None if old_price_str is None else _clear_price(old_price_str)

        return price_dict

def _clear_price(str_pr: str):
    pr = str_pr.replace("грн.", '')
    pr_split = pr.split()
    pr_join = ''.join(pr_split)
    try:
        pr_int = int(pr_join.strip())
    except:
        return 0
    else:
        return pr_int

def _get_top(block_bs: BeautifulSoup):
    try:
        top_tag = block_bs.find('div', {'class': 'gallery_image'}).find('div', {'class': 'hot_image'})
    except:
        print('No tag for top')
        return False
    else:
        if top_tag is None:
            return False
        else:
            return True

def _get_available(block_bs: BeautifulSoup):
    try:
        buy_button_bs = block_bs.find('div', {'class': 'gallery_info item_info'}). \
            find('div', {'class': 'buy-link'}). \
            find('a', {'class': 'buy_button green'})
    except:
        return False
    else:
        if buy_button_bs is None:
            return False
        else:
            return True



# ====================SAVE DATA===================

def _connect_base():
    try:
        conn = pymysql.connect(host='localhost',
                               user='root',
                               passwd='313315',
                               db='sexshop',
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
    except Exception as ex:
        pprint.pprint(ex)
        return None
    else:
        return conn


def write_all_to_mysql():
    print('===========MYSQL===========')
    connect = _connect_base()

    if connect is None:
        print('No connect with mysql')
        return

    cursor = connect.cursor()

    for href_1, dict_2 in ALL_DATA_DICT.items():
        if type(dict_2) is dict:

            for href_2, dict_3 in dict_2.items():
                if type(dict_3) is dict:

                    for href_3, data_list in dict_3.items():
                        if type(data_list) is list:

                            for d in data_list:
                                if type(d) is dict:

                                    values = _get_values(d, href_1, href_2, href_3)
                                    if not values:
                                        continue

                                    writed = _write_line_mysql_from(values, connect, cursor)
                                    if not writed:
                                        continue

    cursor.close()
    connect.close()


def _get_values(d: dict, href_1: str, href_2: str, href_3: str):
    try:
        values = (href_1,
                  href_2,
                  href_3,
                  d['name'],
                  d['href'],
                  d['price'],
                  d['old_price'],
                  d['top'],
                  d['available'])
    except:
        return False
    else:
        return values


def _write_line_mysql_from(values: tuple,
                           connect: pymysql.connections.Connection,
                           cursor: pymysql.cursors.DictCursor):

    query = 'INSERT INTO sexshop_ua ' \
            '(href_1, href_2, href_3, ' \
            'name, link, price, ' \
            'old_price, top, available)' \
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'

    try:
        cursor.execute(query, values)
        connect.commit()
        return True
    except:
        return False


def write_all_to_csv():
    print('===========CSV===========')
    with open('sex_shop_ua.csv', 'w', newline='\n') as file:
        writer = csv.writer(file)

        title = ['href_1', 'href_2', 'href_3', 'name', 'link', 'price', 'old_price', 'top', 'available']
        writer.writerow(title)

        for href_1, dict_2 in ALL_DATA_DICT.items():
            if type(dict_2) is dict:

                for href_2, dict_3 in dict_2.items():
                    if type(dict_3) is dict:

                        for href_3, data_list in dict_3.items():
                            if type(data_list) is list:

                                for d in data_list:
                                    if type(d) is dict:

                                        values = _get_values(d, href_1, href_2, href_3)
                                        if not values:
                                            continue

                                        try:
                                            writer.writerow(values)
                                        except:
                                            continue


if __name__=='__main__':
    url = 'https://sex-shop.ua'
    bs = get_bs_object(url)
    get_menu_links(bs)
    start_pool_process()
    write_all_to_mysql()
    write_all_to_csv()




