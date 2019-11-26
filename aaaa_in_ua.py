import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint


all_dict = dict()
data_list = list()


# main methods
# ============================================
def get_all_links():
    """get href on all category product
        start fill all_dict"""
    bs_obj = get_bs_object('https://aaaa.in.ua/')
    if bs_obj is None:
        return

    blocks_li = find_one_then_all(bs_obj=bs_obj,
                                  tag_one='ul', dict_one={'class': 'first-stage'},
                                  tag_all='li', dict_all={'class': 'first-stage-li'})
    if blocks_li is None:
        return

    for block in blocks_li:
        href = get_href_from_tag(bs_tag=block,
                                 tag_name='a', dict_attr={'class': 'list-group-item active'})
        if href is None:
            continue
        # print('First link: ' + href)
        all_dict[href] = dict()

        stages = find_one_then_all(bs_obj=block,
                                   tag_one='ul', dict_one={'class': 'second-stage'},
                                   tag_all='li', dict_all={'class': 'second-stage-li'})
        if stages is None:
            all_dict[href][href] = list()
            continue

        for block_2 in stages:
            href_2 = get_href_from_tag(bs_tag=block_2,
                                       tag_name='a', dict_attr={'class': 'list-group-item child-first-stage'})
            if href_2 is None:
                continue
            # print('   Second link: ' + href_2 + '?limit=96')
            href_2 = href_2 + '?limit=96'
            all_dict[href][href_2] = list()


def run_all_link():
    global all_dict
    global data_list
    count = 1
    for k1, v1 in all_dict.items():
        count += 1
        print('First link: ' + k1)
        for k2, v2 in v1.items():
            data_list.clear()
            print('    Second link: ' + k2 + str(v2))
            get_data_from_page(url_page=k2)
            all_dict[k1][k2] = data_list.copy()
        # if count == 4:
        #     break


# data from pages
# ============================================
def get_data_from_page(url_page: str):
    """getting data from page
        and go to next page"""
    global data_list
    bs_obj = get_bs_object(url_page)
    if bs_obj is None:
        return None

    forms = bs_obj.find_all('form', {'class': 'category-p'})
    if len(forms) == 0:
        print('No category-p')
        return None
                                                        # get values from one block
    for form in forms:
        data_dict = get_name_and_href(bs_obj=form)
        if data_dict is None: continue
        price_dict = get_price(bs_obj=form)
        data_dict.update(price_dict)
        data_list.append(data_dict)

                                                        # end getting values
    next_link = get_next_link(bs_obj)
    if next_link is not None:
        get_data_from_page(next_link)


def get_name_and_href(bs_obj: BeautifulSoup):
    try:
        tag = bs_obj.find('div', {'class': 'prod_t'}).find('a', {'href': True})
    except Exception as ex_2:
        print('No tag with product-name\n' + str(ex_2))
        return None
    else:
        name = tag.text
        href = tag.get('href')
        return {'name': name, 'href': href}


def get_price(bs_obj: BeautifulSoup):
    data_dict = {'price': None, 'price_old': None}
    try:
        tag = bs_obj.find('div', {'class': 'button-group-price insidepage'}).\
                     find('td', {'class': 'table-price-cell left-price-container'})
    except Exception as ex_2:
        print('No tag with price\n' + str(ex_2))
    else:
        chld = tag.find_all()
        if len(chld) == 0:
            try:
                data_dict['price'] = clear_price(tag.text)
            except Exception as ex_1:
                print('No price\n' + str(ex_1))
        else:
            try:
                data_dict['price_old'] = clear_price(chld[0].text)
                data_dict['price'] = clear_price(chld[1].text)
                percent = get_percent(old=data_dict['price_old'], new=data_dict['price'])
                data_dict['percent'] = percent if percent is not None else True
            except Exception as ex:
                print('No sale\n' + str(ex))
    finally:
        return data_dict


def get_percent(old: str, new: str):
    try:
        old_price = int(old)
        new_price = int(new)
    except:
        print('Percent price (string) not convertible to integer')
        return None
    else:
        percent = ((old_price - new_price) / old_price) * 100
        percent = round(percent, 2)
        return percent


def get_next_link(bs_obj: BeautifulSoup):
    pagination = bs_obj.find('ul', {'class': 'pagination'})
    if pagination is None:
        print('No pagination block')
        return None
    next_link_bs = pagination.find('a', {'rel': 'next', 'href': True})
    if next_link_bs is None:
        print('No pagination next link')
        return None
    next_link = next_link_bs.get('href')
    print('--------NEXT LINK: ' + next_link)
    return next_link


# helpers
# ============================================
def get_bs_object(url: str):
    """universal method for getting bs-object
        if fail - return: None"""
    try:
        html = requests.get(url).content
        bs_obj = BeautifulSoup(html, 'lxml')
    except Exception as ex:
        print('Fail wen getting bs-object from url: ' + url)
        print(ex)
        return None
    else:
        return bs_obj


def find_one_then_all(bs_obj: BeautifulSoup,
                      tag_one: str, dict_one: dict,
                      tag_all: str, dict_all: dict):
    """universal find tags in one tag"""
    first_tag = bs_obj.find(tag_one, dict_one)
    if first_tag is None:
        print('No start tag ' + tag_one + '  with arrt ' + str(dict_one))
        return None
    all_tags = first_tag.find_all(tag_all, dict_all)
    if len(all_tags) == 0:
        print('No all tag ' + tag_all + '  with arrt ' + str(dict_all))
        return None
    return all_tags


def get_href_from_tag(bs_tag: BeautifulSoup, tag_name: str, dict_attr: dict):
    """universal get href from one tag"""
    tag = bs_tag.find(tag_name, dict_attr)
    if tag is None:
        print('No find tag ' + tag_name + ' with attr ' + str(dict_attr))
        return None
    try:
        href = tag.get('href')
    except Exception as ex:
        print(ex)
        print('No href in tag ' + tag_name)
        return None
    else:
        return href


def clear_price(price: str):
    price_clear = price.replace('грн', '').\
                        replace('Цена', ''). \
                        replace(':', ''). \
                        replace('.', '').\
                        replace(',', ''). \
                        replace(' ', ''). \
                        strip()
    return price_clear


def wright_to_file():
    with open('aaaa_json.json', 'w') as writer:
        json.dump(all_dict, writer)
    writer.close()


def output_json():
    js = json.dumps(all_dict, indent=4)
    print(js)


if __name__ == '__main__':
    get_all_links()
    run_all_link()
    output_json()
    wright_to_file()

