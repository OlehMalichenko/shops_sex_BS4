import pymysql
import json
from pprint import pprint


def main():
    dic = get_data_from_file()
    run_on_data(dic)


def connect_to_base():
    try:
        conn = pymysql.connect(host='localhost',
                               user='root',
                               passwd='313315',
                               db='sexshop',
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
    except Exception as ex:
        print(ex)
        return None
    else:
        return conn



def get_data_from_file():
    with open('data_json.json', 'r') as file:
        js = json.load(file)
        dic = dict(js)
    return dic


def run_on_data(dic: dict):
    conn = connect_to_base()
    if conn is not None:
        for k1, v1 in dic.items():
            for k2, v2 in v1.items():
                for k3, v3 in v2.items():
                    for root in v3:
                        root_p = preparation_root(root)
                        query = 'INSERT INTO amurchik ' \
                                '(key1, key2, key3, name, href, articul, ' \
                                'price, old_price, sale, leader, new, no_available)' \
                                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                        values = (k1, k2, k3, root_p['name'], root_p['href'], root_p['articul'],
                                  root_p['price_int'], root_p['old_price_int'], root_p['sale'],
                                  root_p['leader'], root_p['new'], root_p['no_available'])
                        try:
                            conn.cursor().execute(query, values)
                            conn.commit()
                        except Exception as ex:
                            print(ex)
                            continue
            #         break
            #     break
            # break
    else:
        print('No connection')
        return


def preparation_root(root: dict):
    root_p = dict()
    root_p['name'] = root['name'] if root['name'] is not None else 'NoName'
    root_p['href'] = root['href'] if root['href'] is not None else 'NoHref'
    root_p['articul'] = root['articul'] if root['articul'] is not None else 'NoArticul'

    # try price. Check to None and Int
    price = root['price'] if root['price'] is not None else 0
    try:
        root_p['price_int'] = int(price)
    except:
        root_p['price_int'] = 1

    # try old_price. Check to None and Int
    old_price = root['old_price'] if root['old_price'] is not None else 0
    try:
        root_p['old_price_int'] = int(old_price)
    except:
        root_p['old_price_int'] = 1

    # try sale. Check to available in root
    try:
        root_p['sale'] = root['sale']
    except:
        root_p['sale'] = None

    # try leader. Check to available in root
    try:
        root_p['leader'] = root['leader']
    except:
        root_p['leader'] = None

    # try new. Check to available in root
    try:
        root_p['new'] = root['new']
    except:
        root_p['new'] = None

    # try new. Check to available in root
    try:
        root_p['no_available'] = root['no_available']
    except:
        root_p['no_available'] = None

    return root_p


if __name__ == '__main__':
    main()


