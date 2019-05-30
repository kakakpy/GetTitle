#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Description: todo
# @author: kakak~~
# Created on 2018年7月26日下午8:54:28
# @version V1.0

# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import threading
import Queue
import time
import sys
import os
import chardet

reload(sys)
sys.setdefaultencoding('utf-8')


def decode_response_text(txt, charset=None):
    if charset:
        try:
            return txt.decode(charset)
        except Exception as e:
            pass
    for _ in ['UTF-8', 'GB2312', 'GBK', 'iso-8859-1', 'big5']:
        try:
            return txt.decode(_)
        except Exception as e:
            pass
    try:
        return txt.decode('ascii', 'ignore')
    except Exception as e:
        pass
    raise Exception('Fail to decode response Text')



#去重去空格去空列表元素
def removal(removal):
    news_ids = []
    for id in removal:
        if id.rstrip() not in news_ids and id.rstrip() !='' :
            news_ids.append(id.rstrip())
            print id.rstrip()
    print "removal:" + str(len(removal) - len(news_ids))
    return news_ids


# schema http://或者https://
def request_title(schema, domain):


    url= schema + domain
    print url+'\n'
    try:
        requests.packages.urllib3.disable_warnings()
        http = requests.get(url, timeout=5, verify=False)

        title = BeautifulSoup(decode_response_text(http.content), features="html.parser",).title
        if title is None:
            title = "title is blank"
        else:
            title = title.text.strip()

        status = str(http.status_code)

    except:
        title =" ---cannot access--- "
        status = "time out"
    finally:
        return schema, domain, title, status



def getTitle(domain):
    schema, domain, title, status = request_title("http://",domain)
    if status =="time out":
        schema, domain, title, status = request_title("https://", domain)

    line = "\t".join([schema, domain, title, status])
    print line
    return line


class MyThread(threading.Thread):

    def __init__(self, queue,result):
        threading.Thread.__init__(self)
        self.queue = queue
        self.result = result

    def run(self):
        while True:
            domainlist = self.queue.get()
            line=getTitle(domainlist)
            self.result.append(line)
            self.queue.task_done()


def title_run(l,result_name,ts=40):
    allresult = []

    list = removal(l)  # 去重
    for j in range(ts):
        t = MyThread(queue, allresult)
        t.setDaemon(True)
        t.start()

    for url in list:
        queue.put(url)
    queue.join()

    with open("result-" + result_name, 'w') as s:
        s.writelines(allresult)



if __name__ == '__main__':

    domain_file = str(sys.argv[1]) if len(sys.argv)>1 else "get_http_title.txt"  #自定义扫描文件。
    with open(domain_file) as f:
        l = f.readlines()

    queue = Queue.Queue()
    start = time.time()
    title_run(l,os.path.basename(domain_file),80)
    end = time.time()
    print 'Total time consuming:%ss' % (end - start)
