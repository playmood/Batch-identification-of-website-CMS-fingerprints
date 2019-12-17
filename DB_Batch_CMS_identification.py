#! /usr/bin/env python
#by www.teamssix.com
import sys
import zlib
import json
import pymongo
import requests
import pandas as pd

def whatweb(url):
    response = requests.get(url,headers = headers,verify=False,allow_redirects=False,timeout=1) #如果本地网络环境延时较高，timeout可设置高一些，默认为1s
    whatweb_dict = {"url":response.url,"text":response.text,"headers":dict(response.headers)}
    whatweb_dict = json.dumps(whatweb_dict)
    whatweb_dict = whatweb_dict.encode()
    whatweb_dict = zlib.compress(whatweb_dict)
    data = {"info":whatweb_dict}
    return requests.post("http://whatweb.bugscaner.com/api.go",headers = headers,allow_redirects=False,files=data,timeout=1)  #如果本地网络环境延时较高，timeout可设置高一些，默认为1s
    
def results(url,title):
    result = {}
    request = whatweb(url)
    num = request.headers["X-RateLimit-Remaining"]
    print(u"\n\033[1;33;40m[!] 今日识别剩余次数 {},正在识别 {}\033[0m".format(num,url))
    req_json = request.json()
    for i in req_json:
        sub_i = req_json[i][0]
        result[i] = sub_i
    result['URL'] = url
    result['title'] = title
    return result

if __name__ == '__main__':
    pools = []
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
    try:
        file_name = sys.argv[1]
        client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
        db = client['domain']
        col = db["{}".format(file_name)]
        url_list = []
        title_list = []
        for i in col.find({},{'url'}):
            url_list.append(i['url'])
        for i in col.find({},{'title'}):
            title_list.append(i['title'])
    except:
        print('''\033[1;31;40m
请检查你的参数是否有误

示例：python3 DB_Batch_CMS_identification.py db_name
eg:   python3 DB_Batch_CMS_identification.py _ctrip_com
        \033[1;31;40m''')
        sys.exit()
    
    print('''\n\033[1;33;40m
示例：python3 DB_Batch_CMS_identification.py db_name
eg:   python3 DB_Batch_CMS_identification.py _ctrip_com
        \033[0m''')

    for numbers in range(len(url_list)):
        try:
            pools.append(results(url_list[numbers],title_list[numbers]))
        except (requests.exceptions.ConnectionError,requests.exceptions.ReadTimeout):
            print('\033[1;31;40m[-] 连接异常，正在识别下一个URL……\033[0m')
            pass
        except BaseException as e:
            print('\033[1;31;40m[-] 程序发生'+str(e)+'异常','正在保存退出……\033[0m')
            sys.exit()
        finally:
            df = pd.DataFrame(pools)
            df.to_csv(r'{}.csv'.format(file_name),encoding='GB2312')
