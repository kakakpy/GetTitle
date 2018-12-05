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

reload(sys)
sys.setdefaultencoding('utf-8')


#去重去空格去空列表元素
def removal(removal):
    news_ids = []
    for id in removal:
        if id.rstrip() not in news_ids and id.rstrip() !='' :
            news_ids.append(id.rstrip())
            print id.rstrip()
    print "去重数:" + str(len(removal) - len(news_ids))
    return news_ids


# schema http://或者https://
def request_title(schema,domain):
    url= schema+ domain
    print url+'\n'
    requests.packages.urllib3.disable_warnings()
    http = requests.get(url, timeout=5, verify=False)
    http.encoding = 'gb2312'  # 这个编码不会错
    soup = BeautifulSoup(http.content, "html5lib")
    title = soup.title.text
    status = str(http.status_code)

    return schema, domain, title.strip(), status



def getTitle(domain):
    try:
        schema, domain, title, status=request_title("http://",domain)

    except:
        try:
            schema, domain, title, status=request_title("https://",domain)
        except:
            schema="ALL"
            title='null--'
            status = "time out"
    line = schema + '\t' + domain + '\t' + title + '\t' + status + '\n'
    #result.append(line)
    return line


class MyThread(threading.Thread):

    def __init__(self, queue,result):
        threading.Thread.__init__(self)
        self.queue = queue
        self.result=result

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
        t = MyThread(queue,allresult)
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
