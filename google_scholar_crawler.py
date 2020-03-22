#coding:utf8

'''Google Scholar Crawler

contact: chenwc18@mails.tsinghua.edu.cn

requires:
    1. 能 ping 通 scholar.google.com
    2. python3 以及必要的包

功能：
    给定一个 paper list ，爬取 Google Scholar 上每篇 paper 的被引用文章列表，将其 title author year 保存在 csv 文件中

用法：
    1. 将要爬取的 paper 名字保存在 paper_list.txt 中，每个名字独占一行
    2. 运行 python google_scholar_crawler.py 即可在 results 文件夹中得到结果

注意：
    1. Google Scholar 的反爬机制比较厉害，本脚本可能失效
    2. 如果运行中出现问题，可以查看 debug.html 观察是否被反爬了
'''

from urllib.parse import quote
import urllib.parse
import urllib.request as request
from bs4 import BeautifulSoup

import re
import time
import os
import random


def write_txt(filename, res):
    with open(filename, 'w', encoding='utf-8') as fw:
        for id, r in enumerate(res):
            title, author, year = r
            fw.write('{id}{title}\t{author}\t{year}\n'.format(id=id+1, title=title, author=author, year=year))

def write_csv(filename, res):
    import csv
    with open(filename,'w', newline='', encoding='utf-8-sig') as f:
        csv_write = csv.writer(f)
        for id, r in enumerate(res):
            r.insert(0, str(id+1))
            csv_write.writerow(r)

def get_html(url):
    header_dict={'Host': 'scholar.google.com',
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
             'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
             'Referer': 'https://scholar.google.com/schhp?hl=zh-CN',
             'Connection': 'keep-alive'}

    req = urllib.request.Request(url=url,headers=header_dict)
    response = urllib.request.urlopen(req,timeout=3)
    html = response.read()
    with open('debug.html', 'wb') as f:
        f.write(html)

    print("conneect succeed!")
    return html

def parse_first(html):
    soup = BeautifulSoup(html, 'html.parser')
    # con = soup.find_all(attrs={'class': 'gs_fl'})[1]
    if len(soup.find_all(attrs={'class': 'gs_ri'})) == 0:
        return None, 0
    if len(soup.find_all(attrs={'class': 'gs_ri'})[0].find_all(attrs={'class': 'gs_fl'})) == 0:
        return None, 0
    con = soup.find_all(attrs={'class': 'gs_ri'})[0].find_all(attrs={'class': 'gs_fl'})[0]
    next_url = con.find_all('a')[2].get('href')
    cite_num = int(con.find_all('a')[2].getText().split('：')[-1])
    next_url = 'https://scholar.google.com/' + next_url
    return next_url, cite_num

def parse(html):
    # soup = BeautifulSoup(open('test.htm'), 'html.parser')
    soup = BeautifulSoup(html, 'html.parser')
    contents = soup.find_all(attrs={'class': 'gs_ri'})
    res = []
    for con in contents:
        title = con.find_all('a')[0].getText()
        title_a = con.find_all(attrs={'class':'gs_rt'})[0].find_all('a')
        if len(title_a) == 0:
            title = con.find_all(attrs={'class':'gs_rt'})[0].getText().split(']')[-1]
        else:
            title = title_a[0].getText()
        author_pro_year_url = con.find_all(attrs={'class': 'gs_a'})[0].getText().replace('\xa0', '')
        author = author_pro_year_url.split('- ')[0]
        year = author_pro_year_url.split('- ')[1].split(',')[-1]
        print('title: ', title)
        # print('author: ', author)
        # print('year: ', year)
        tmp = [title, author, year]
        res.append(tmp)
    next = soup.find_all(attrs={'id': 'gs_n'})[0].find_all('a')[-1]
    if next.getText() == '下一页':
        next_url = 'https://scholar.google.com/' + next.get('href')
    else:
        next_url = None
    return res, next_url

def do_ugly(filename, url_base, num):
    res = []
    for i in range(num):
        url = url_base.format(10*i)
        print('Processing {}: {}'.format(i, url))
        html = get_html(url)
        res_tmp, next_url = parse(html)
        res += res_tmp
        t = random.randint(50, 200)/10.
        time.sleep(t) # 防止被封
    write_csv(filename, res)

def go_ugly():
    filenames = [
        'result.csv'
    ]
    url_bases = [
        'https://scholar.google.com/scholar?start={}&hl=zh-CN&as_sdt=2005&sciodt=0,5&cites=9518624311113000520&scipsc=',
    ]
    nums = [
        11
    ]
    for filename, url_base, num in zip(filenames, url_bases, nums):
        do_ugly(filename, url_base, num)


def test():
    html = open('test.htm')
    res = parse(html)
    filename = 'test.csv'
    write_csv(filename, res)
    filename = 'test.txt'
    # write_txt(filename, res)


def do_elegant(filename, next_url):
    res = []
    while next_url:
        print('Processing url: {}'.format(next_url))
        html = get_html(next_url)
        res_tmp, next_url = parse(html)
        res += res_tmp
        t = random.randint(100, 200)/10.
        time.sleep(t) # 防止被封
    write_csv(filename, res)

def go_elegant():
    dirname = 'results/'
    if os.path.exists(dirname):
        os.rmdir(dirname)
    os.makedirs(dirname)
    def get_paper_list(listname='paper_list.txt'):
        with open(listname) as f:
            paper_list = f.readlines()
        return [paper.strip() for paper in paper_list]

    # paper_list = [
    #     'Sparse LU factorization for parallel circuit simulation on GPU',
    #     'Technological Exploration of RRAM Crossbar Array For Matrix-Vector Multiplication'
    # ]
    paper_list = get_paper_list()
    url_base = 'https://scholar.google.com/scholar?hl=zh-CN&as_sdt=0%2C5&q={}&btnG='
    for paper in paper_list:
        print('Start processing paper: ', paper)
        url = url_base.format(quote(paper))
        next_url, cite_num = parse_first(get_html(url))
        if not next_url:
            continue
        filename = dirname+'{}.csv'.format(paper.replace(' ', '_'))
        do_elegant(filename, next_url)
        print('Done processing paper: ', paper)


if __name__ == '__main__':
    # test()
    go_elegant()

