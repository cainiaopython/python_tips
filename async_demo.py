# # -*- coding: utf-8 -*
'''
通过一个简单的爬虫案例，来对Python的几种并发过程进行示例
详情并发介绍可见,微信公众号"菜鸟学Python"，目前原创160多篇
author:leoxin 
'''
from pyquery import PyQuery as pq
from requests.exceptions import ConnectTimeout
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from threading import Thread
from multiprocessing import Pool
import requests
import time
import queue
import gevent
import os
import random

COUNT = 1


# connect the webpage and crawl it
def connect(args):
    global COUNT
    print('Run task in %s.' % os.getpid())
    output = {}
    url_base,word=args
    url = '{}/{}'.format(url_base, word)
    print('{}:Parse:{}'.format(COUNT, url))

    try:
        r = requests.get(url)
        html_cont = r.text
        desc = parse_url(html_cont)
        COUNT += 1
    except ConnectTimeout as e:
        print('Get url:{} timeout'.format(url))
    except ConnectionError as e:
        print('Get url:{} error'.format(url))
    except Exception as e:
        print(e)

    output['Word'] = word
    output = dict(output, **desc)
    # print(output)
    return output


# parse the page
def parse_url(doc):
    info = {}
    info['Desc'] = ''
    doc = pq(doc)
    items = list(doc.items('.mw-parser-output .hatnote'))
    if len(items) > 1:
        info['Desc'] = items[0].text()
    return info


# computer the program running time
import time


def cost_time(func):
    def wrap(*args):
        s = time.time()
        func(*args)
        print('Cost:{}'.format(time.time() - s))

    return wrap


# sync task
@cost_time
def sync_task(fun, *args):
    url_base, words = args
    for word in words:
        res = fun((url_base, word))
        print(res)


def handle_threads(queue):
    while not queue.empty():
        args = queue.get()
        print('args:', args)
        res = connect(args)
        print(res)


def task(url):
    r = requests.get(url)
    doc = pq(r.text)
    items = doc('#questions .question-summary').items()
    for item in items:
        title = item.find('.summary h3').text()
        views = item.find('.views').text()
        print('Title:{}, views:{}'.format(title, views))


def split_line(des):
    print('-' * 20 + des + '-' * 20)


@cost_time
def async_by_threadsPool(fun, *args):
    q = queue.Queue()
    url_base, words = args
    for word in words:
        q.put((url_base, word))

    threads_pool = [Thread(target=handle_threads, args=(q,)) for i in range(3)]
    for t in threads_pool:
        t.start()
        print('running thread{}'.format(t.getName()))
    for t in threads_pool:
        t.join()


@cost_time
def async_task_by_threadingPoolExecutor(fun, *args):
    pool = ThreadPoolExecutor(3)
    url_base, words = args
    threads = [pool.submit(fun, (url_base, word)) for word in words]
    outputs = []
    for t in threads:
        print(t.result()) if t.result() else None


@cost_time
def async_task_by_ProcessPoolExecutor(fun, *args):
    pool = ProcessPoolExecutor(3)
    url_base, words = args
    processes = [pool.submit(fun, (url_base, word)) for word in words]
    outputs = []
    for p in processes:
        print(p.result()) if p.result() else None


@cost_time
def async_task_by_gevent(fun, *args):
    print('Start async by gevent')
    url_base, words = args
    events = [gevent.spawn(fun, (url_base, word)) for word in words]
    wordinfos = gevent.joinall(events)
    for wordinfo in wordinfos:
        print(wordinfo.get())


def use_gevent():
    import gevent.monkey
    gevent.monkey.patch_all()
    split_line('Use Gevent')
    async_task_by_gevent(connect, url_base, words)


@cost_time
def async_task_by_ProcessPoolMap(fun,*args):
    print('Parent process %s.' % os.getpid())
    url_base,words=args
    with Pool(4) as p:
        for word in words:
            result=p.map(fun,((url_base,word),))
            print (result)



if __name__ == '__main__':
    words = ['China', 'America', 'England', 'France', 'Germany']
    url_base = 'https://en.wikipedia.org/wiki'

    split_line('Use Sync')
    sync_task(connect, url_base,words)

    split_line('Use multiprocess pools')
    async_task_by_ProcessPoolMap(connect,url_base,words)

    split_line('Use Async multi-process pools')
    async_task_by_ProcessPoolExecutor(connect,url_base,words)

    # split_line('Use Async multi-threads pools')
    # async_task_by_threadingPoolExecutor(connect,url_base,words)

    # split_line('User manual threads pools')
    # async_by_threadsPool(connect,url_base,words)

    # use_gevent()
