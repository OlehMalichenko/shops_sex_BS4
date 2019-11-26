import requests
from bs4 import BeautifulSoup
import json
from random import uniform
from time import sleep


all_dict = dict()
data_list = list()


def get_all_links(url: str):
    global all_dict
    html = requests.get(url).content
    bs = BeautifulSoup(html, 'lxml')
    bs_items = bs.findAll('li', {'class': 'firstLevel', 'id': True})

    for item in bs_items:
        level_1 = item.find('a', {'class': 'firstLevel', 'href': True}).get('href')
        all_dict[level_1] = dict()
        menu_col = item.findAll('div', {'class': 'menu-col'})

        for menu in menu_col:
            children = menu.find_all(recursive=False)

            for child in children:
                if child['class'][0] == 'second-parent':
                    continue
                elif child['class'][0] == 'first':
                    level_2 = child.find('a', {'href': True}).get('href')
                    all_dict[level_1][level_2] = dict()
                    try:
                        second_parent = child.find_next_sibling()
                        check_next = second_parent['class'][0]
                    except:
                        check_next = None
                    if check_next is not None and check_next == 'second-parent':
                        seconds = second_parent.find_all(recursive=False)
                        for second in seconds:
                            level_3 = second.find('a', {'href': True}).get('href')
                            all_dict[level_1][level_2][level_3] = list()
                    else:
                        all_dict[level_1][level_2][level_2] = list()
    # print_dict(all_dict)
    write_json_to_file(all_dict)


def run_on_all_dict_and_work():
    global data_list
    global all_dict
    for key, value in all_dict.items():                 # level 1
        if type(value) == dict:
            for k2, v2 in value.items():                # level 2
                if type(v2) == dict:
                    for k3, v3 in v2.items():           # target level 3. k3 - start link from work_to_prodact_list
                        if type(v3) == list:
                            data_list.clear()           # data_list must be empty
                            start_link = 'https://amurchik.ua' + k3
                            print(start_link)
                            work_to_prodact_list(start_link)
                            all_dict[key][k2][k3] = data_list.copy()
                            # sleep(uniform(1, 3))


def write_json_to_file(all_dict: dict):
    with open('data_json.json', 'w') as writer:
        json.dump(all_dict, writer)
    writer.close()


def data_print(data: list):
    for el in data:
        print(el['name'])
        print(el['href'])
        print(el['articul'])
        print(el['price'])
        print(el['old_price'])
        print(el['sale'])
        print(el['leader'])
        print(el['new'])
        print(el['no_available'])


def work_to_prodact_list(url):
    global data_list
    # start trying
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    try:
        html = requests.get(url, headers=headers).content
        bs = BeautifulSoup(html, 'lxml')
        blocks = bs.find('div', {'id': 'listTovars'}).find_all('div', {'class': 'prod-item'})
    except:
        return

    for num, block in enumerate(blocks):
        dic = dict()
        dic['name'] = get_name(bs=block)
        dic['href'] = get_href(bs=block)
        dic['articul'] = get_articul(bs=block)
        dic['price'] = get_price(bs=block)
        dic['old_price'] = get_price(bs=block, old=True)
        posb_data = get_posab_data(bs=block)
        dic['sale'] = posb_data['sale'] if posb_data is not None else None
        dic['leader'] = posb_data['leader'] if posb_data is not None else None
        dic['new'] = posb_data['new'] if posb_data is not None else None
        dic['no_available'] = get_status_available(bs=block)
        data_list.append(dic)
    # url for next product-list
    next_list_product = get_next_page(bs)
    if next_list_product is not None:
        print('Next link in block:  ' + next_list_product)
        print('sleep')
        # sleep(uniform(0.2, 1))
        work_to_prodact_list(next_list_product)


def get_name(bs: BeautifulSoup):
    try:
        title_name = bs.find('a', {'class': 'index_product'}).text
    except:
        title_name = None
    else:
        title_name = title_name.strip()
    finally:
        return title_name


def get_href(bs: BeautifulSoup):
    try:
        href = bs.find('a', {'class': 'index_product'}).get('href')
    except:
        href = None
    else:
        href = 'https://amurchik.ua' + href.strip()
    finally:
        return href


def get_articul(bs: BeautifulSoup):
    articul = str()
    try:
        articul_bs_list = bs.find('li', {'class': 'articul'}).find_all('span')
    except:
        return None
    else:
        if len(articul_bs_list) == 0:
            return None
        else:
            articul = articul_bs_list[len(articul_bs_list) - 1].text
    finally:
        return articul.strip()


def get_price(bs: BeautifulSoup, old=False):
    attr = 'old-price' if old else 'price'
    try:
        price = bs.find('div', {'class': 'buy'}).find('span', {'class': attr}).text
    except:
        price = None
    else:
        price = price.strip('грн').strip()
    finally:
        return price


def get_posab_data(bs: BeautifulSoup):
    dic = dict()
    posab_block = bs.find('div', {'class': 'posabs'})
    if posab_block is not None:
        dic['sale'] = check_posab(posab_block, 'div', {'class': 'posab sale-posab'})
        dic['leader'] = check_posab(posab_block, 'div', {'class': 'posab leader-posab'})
        dic['new'] = check_posab(posab_block, 'div', {'class': 'posab new-posab'})
    else:
        dic = None
    return dic


def check_posab(bs_obj: BeautifulSoup, tag_name: str, dict_attr: dict):
    result = False
    check = bs_obj.find(tag_name, dict_attr)
    if check is not None:
        result = True
    return result


def get_status_available(bs: BeautifulSoup):
    no_available = True
    try:
        bs.find('div', {'class': 'small-prods clearfix'}).find('div', {'class': 'small-prods-text'}).text
    except:
        no_available = False
    finally:
        return no_available


def get_next_page(bs_obg: BeautifulSoup):
    try:
        href = bs_obg.find('div', {'class': 'pager'}). \
            find('a', {'class': 'no_underline btn next-btn'}).get('href')
        next_url = 'https://amurchik.ua' + href
    except:
        next_url = None
    return next_url



# ////////////////////////////////////////////////////
if __name__ == '__main__':
    get_all_links('https://amurchik.ua/mainmenu.php')
    all_dict.clear()
    with open('data_json.json', 'r') as file:
        js = json.load(file)
        all_dict = dict(js)
        run_on_all_dict_and_work()
    file.close()
    with open('data_json.json', 'w') as file_write:
        json.dump(all_dict, file_write)
    file_write.close()