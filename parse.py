'''Google Scholar Parsing

contact: chenwc18@mails.tsinghua.edu.cn

功能：
    这个脚本可以用来解析某篇文章的被引用文章列表，会将被引用文章的title、author、year保存在csv文件中

用法:
    1. 到浏览器中把某篇文章的被引用文章列表页面保存在 htmls/ 这个文件夹下，按页面依次保存成 1.html 2.html 3.html ...
    2. 按需要修改 do 函数中第49行和第59行
    3. 运行 python parse.py 即可在保存的csv文件中得到结果

'''

from bs4 import BeautifulSoup
import os

def write_csv(filename, res):
    import csv
    with open(filename,'w', newline='', encoding='utf-8-sig') as f:
        csv_write = csv.writer(f)
        for id, r in enumerate(res):
            r.insert(0, str(id+1))
            csv_write.writerow(r)

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
    next_url = None
    return res, next_url

def do():
    def get_list():
        html_list = []
        for i in range(1, 12): # 在这里修改要解析哪些页面
            path = 'htmls/{}.html'.format(i)
            if os.path.exists(path):
                html_list.append(path)
        return html_list
    html_list = get_list()
    res = []
    for html in html_list:
        tmp, _ = parse(open(html))
        res += tmp
    print('{} papers in total'.format(len(res)))
    filename = '8.csv' # 在这里修改保存的文件名
    write_csv(filename, res)

if __name__ == '__main__':
    do()


