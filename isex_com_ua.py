from multiprocessing import Pool
from bs4 import BeautifulSoup
import requests
import pymysql
import pprint
import csv
import re


ALL_DATA_DICT = dict()  # keys - main menu links; values - dicts


def _get_BSobject_from(url: str):
    u_a = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
    try:
        response = requests.get(url=url, headers=u_a)
    except Exception as ex:
        print(ex)
        return None
    else:
        if response.status_code != 200:
            return None
    html = response.text
    bs_obj = BeautifulSoup(html, 'lxml')
    return bs_obj



# ======================GET MENU LINKS TO ALL_DATA_DICT ====================

def get_menu_links_from(url: str):
    global ALL_DATA_DICT
    """begin run on the start page and get menu links"""
    bs_obj = _get_BSobject_from(url=url)

    if bs_obj is None:
        print('No connect from start-url: ' + url)
        return

    try:
        menu = bs_obj.find('ul', {'id': 'menu'}).\
                      find_all('li', {'class': 'nd'})
    except Exception as ex:
        print(str(ex) + '\n' +
              'not find UL with ID=MENU of LI with CLASS=ND' + '\n' +
              'Link: ' + url)
    else:
        for node_bs in menu:
            try:
                href = node_bs.find('a', {'href': True}).get('href')
            except Exception as ex:
                print(ex)
                continue
            else:

                """MAIN WORK"""
                link_1 = url + href                         # complete link_1
                ALL_DATA_DICT[link_1] = dict()
                _get_links2_from(link_1)              # in this method to ALL_DATA_DICT append next level
                print(link_1)
                """END MAIN WORK"""


def _get_links2_from(url: str):
    global ALL_DATA_DICT

    bs_obj = _get_BSobject_from(url=url)

    if bs_obj is None:
        print('No connect from link-1: ' + url)
        return

    try:
        menu = bs_obj.find('ul', {'id': 'menu'}).\
                      find('li', {'class': 'act_nd'}).\
                      find_all('li', {'class': 'nch'})

    except Exception as ex:
        print(str(ex) + '\n' + 'not find UL with ID=MENU or LI with CLASS=ACT_ND  CLASS=NCH' + '\n' + 'Link: ' + url)
        return

    else:

        if len(menu) == 0:
            link_2 = url + '?show_all=yes'          # complete link_2 alternative
            ALL_DATA_DICT[url][link_2] = list()
            print('        ' + link_2)
            return

        for nch_bs in menu:

            try:
                href = nch_bs.find('a', {'class': 'childnode', 'href': True}).get('href')

            except Exception as ex:
                print(ex)
                continue

            else:

                """MAIN WORK"""
                link_2 = 'https://isex.com.ua' + href + '?show_all=yes'       # complete link_2
                ALL_DATA_DICT[url][link_2] = list()
                print('        ' + link_2)
                """END MAIN WORK"""

"""result: filling ALL_DATA_DICT menu-links (link_1 and link_2)"""



# ======================DIRECTLY WORK WITH BLOCKS=======================

def _get_list_tuples_for_pool():
    global ALL_DATA_DICT
    list_with_tuples = list()
    for link_1, links_2 in ALL_DATA_DICT.items():
        for link_2 in links_2:
            tuple_for_list = (link_2, link_1)
            list_with_tuples.append(tuple_for_list)
    # pprint.pprint(list_with_tuples)
    return list_with_tuples


def work_pool_with_blocks():
    print('\n\n\n ====================================START POOL=====================================')
    list_with_tuples = _get_list_tuples_for_pool()
    pool = Pool(40)
    result = pool.map(_work_with_pages, list_with_tuples)
    _parse_result_from_pool(result)
    print('\n\n\n END POOL=====================================')


def _work_with_pages(links_tuple: tuple):
    try:
        link_2 = links_tuple[0]
        link_1 = links_tuple[1]
    except Exception as ex:
        print(ex)
        return

    data_list = _get_data_from_page(link_2)

    dic = {link_1: {link_2: data_list}}
    return dic


def _get_data_from_page(url: str):
    bs_obj = _get_BSobject_from(url)

    if bs_obj is None:
        print('No connect from url: ' + url)
        return None

    try:
        blocks_bs = bs_obj.find('ul', {'id': 'products'}).\
                           find_all('li', {'class': 'clearfix all_products'})
    except Exception as ex:
        print(ex)
        return None
    else:

        """MAIN"""
        if len(blocks_bs) == 0:
            return None

        data_list = list()

        for block_bs in blocks_bs:
            dic_one_block = _work_with_one_block(block_bs)
            data_list.append(dic_one_block)

        next_page_url = _get_next_page_url(bs_obj)

        if next_page_url is not None:
            next_data_list = _get_data_from_page(next_page_url)

            if next_data_list is not None:
                data_list.extend(next_data_list)
                print('                 ' + next_page_url)
        return data_list


def _work_with_one_block(block_bs: BeautifulSoup):
    dic = dict()
    dic['name'] = _get_name(block_bs)
    dic['href'] = _get_href(block_bs)
    dic['price'] = _get_price(block_bs)
    dic['available'] = _get_available(block_bs)
    dic['recommend'] = _get_recommend(block_bs)
    return dic


def _get_next_page_url(bs_obj: BeautifulSoup):
    try:
        href = bs_obj.find('div', {'class': 'iscenterblock'}).\
                      find('span', {'class': 'red isfont12'}).\
                      find('a', text=re.compile('^>$')).\
                      get('href')
    except:
        return None
    else:
        return 'https://isex.com.ua' + href


def _parse_result_from_pool(res: list):
    print('\n\n\n PARSE POOL RESULT=====================================')

    for dict_1 in res:
        if type(dict_1) is not dict:
            pprint.pprint(dict_1)
            continue

        for link_1, link_2_dic in dict_1.items():
            if type(link_2_dic) is not dict:
                pprint.pprint(link_2_dic)
                continue

            for link_2, data_list in link_2_dic.items():
                if type(data_list) is not list:
                    pprint.pprint(data_list)
                    continue
                ALL_DATA_DICT[link_1][link_2] = data_list

"""result: get needed data and filling ALL_DATA_DICT"""



# =============DATA FROM ONE BLOCK==================

def _get_name(block_bs: BeautifulSoup):
    try:
        name = block_bs.find('div', {'class': 'product-name'}).find('a', {'href': True}).text
    except Exception as ex:
        print(ex)
        return None
    else:
        return name

def _get_href(block_bs: BeautifulSoup):
    try:
        href = block_bs.find('div', {'class': 'product-name'}).\
                        find('a', {'href': True}).get('href')
    except Exception as ex:
        print(ex)
        return None
    else:
        return 'https://isex.com.ua' + href

def _get_price(block_bs: BeautifulSoup):
    try:
        price_str = block_bs.find('div', {'class': 'prod-price'}).text
    except Exception as ex:
        print(ex)
        return None
    else:
        price = _get_price_int_from(price_str)
        return price

def _get_price_int_from(price_str: str):
    try:
        price_int = int(price_str)
    except:
        price_clear = price_str.replace('грн', ''). \
            replace('Цена', ''). \
            replace(':', ''). \
            replace('.', ''). \
            replace(',', ''). \
            replace(' ', ''). \
            strip()
        try:
            price_int = int(price_clear)
        except:
            return 0
        else:
            return price_int
    else:
        return price_int

def _get_available(block_bs: BeautifulSoup):
    try:
        avail = block_bs.find('div', {'class': 'sklad'}).find('span', {'class': 'green'}).text
    except:
        return False
    else:
        return True

def _get_recommend(block_bs: BeautifulSoup):
    try:
        rec = block_bs.find('div', {'class': 'vyb_novynka'}).find('img', {'class': {'vibor'}}).get('alt')
    except:
        return False
    else:
        return True

"""result: hendler for getting data from one block"""



# ==============WORK WITH DATABASE==================

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


def write_to_mysql():
    print('\n\n\n ====================================MYSQL=====================================')
    conn = _connect_base()

    if conn is None:
        write_to_csv()
        return

    cur = conn.cursor()

    for link_1, link_2_dict in ALL_DATA_DICT.items():

        for link_2, data_list in link_2_dict.items():

            for d in data_list:

                query = 'INSERT INTO isex ' \
                        '(link_1, link_2, name, href, price, available, recomend)' \
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)'

                values = (link_1,
                          link_2,
                          d['name'],
                          d['href'],
                          d['price'],
                          d['available'],
                          d['recommend'])

                try:
                    cur.execute(query, values)
                    conn.commit()

                except Exception as ex:
                    pprint.pprint(ex)
                    continue

    cur.close()
    conn.close()


def write_to_csv():
    print('\n\n\n ====================================CSV=====================================')
    with open('csv_isex.csv', 'w', newline='\n') as csv_file:
        writer = csv.writer(csv_file)

        title_data = ['link_1', 'link_2', 'name', 'href', 'price', 'available', 'recommend']
        writer.writerow(title_data)

        for link_1, link_2_dic in ALL_DATA_DICT.items():

            for link_2, data_list in link_2_dic.items():

                for d in data_list:

                    line_list = [
                        link_1,
                        link_2,
                        d['name'],
                        d['href'],
                        d['price'],
                        d['available'],
                        d['recommend']
                    ]

                    try:
                        writer.writerow(line_list)
                    except:
                        continue




if __name__ == '__main__':
    get_menu_links_from('https://isex.com.ua')
    work_pool_with_blocks()
    write_to_csv()
    write_to_mysql()
