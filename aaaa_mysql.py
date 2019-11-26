import pymysql
import json
import pprint


def main():
    dict_data = get_data_from_file()
    run_on_dict(dict_data)


def connect():
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
    with open('aaaa_json.json', 'r') as file:
        js = json.load(file)
        dic = dict(js)
    return dic


def run_on_dict(dic: dict):
    conn = connect()
    if conn is not None:
        for k1, v1 in dic.items():
            if type(v1) is dict:
                for k2, v2 in v1.items():
                    if type(v2) is list and len(v2) != 0:
                        for root in v2:
                            if type(root) is dict:
                                query = 'INSERT INTO aaaa ' \
                                        '(key1, key2, name, href, price, price_old, percent)' \
                                        'VALUES (%s, %s, %s, %s, %s, %s, %s)'
                                try:
                                    percent = root['percent']
                                except:
                                    percent = 0

                                values = (k1, k2, root['name'], root['href'],
                                          trying_to_int(root['price']),
                                          trying_to_int(root['price_old']),
                                          trying_to_int(percent))

                    # break
            # break

                                try:
                                    conn.cursor().execute(query, values)
                                    conn.commit()
                                except Exception as ex:
                                    print(ex)
                                    continue

    else:
        print('No connect')
        return


def trying_to_int(this):
    if type(this) is int:
        return this
    if this is None:
        return 0
    try:
        result = int(this)
    except ValueError as ve:
        return 0
    return result


def put_data_to_base():
    pass


if __name__ == '__main__':
    main()