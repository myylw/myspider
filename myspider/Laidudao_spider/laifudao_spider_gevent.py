import gevent
from gevent import monkey

monkey.patch_all()
import requests
import re
import os


class LaifudaoSpider:
    url_head, url_tail = 'http://www.laifudao.com/index_', '.htm'
    pic_filename = ('jpg', 'gif', 'jpeg', 'png', 'bmp')
    regex = re.compile(r'<img alt="(?P<title>[^"]+)" src="(?P<src>http://down[0-9].laifudao.com/tupian/\d*.\w{3,4})"')

    def __init__(self, start, end, path):
        self.start_page, self.end_page = start, end
        self.page_gen = self.page_add()
        self.path = path

    def path_check(self):
        if os.path.exists(self.path) is False:
            os.makedirs(self.path)
            print('mkdir ', self.path)

    def page_add(self):
        for page_num in range(self.start_page, self.end_page + 1):
            yield self.url_head + str(page_num) + self.url_tail

    def page_load(self, url):
        # print('page_re', url)
        try:
            response = requests.request('GET', url, timeout=10).content.decode('utf-8')
        except Exception as e:
            print(e)

        result = self.regex.finditer(response)
        for img_url in result:
            pic_src = img_url.groupdict()['src']
            if pic_src.split('.')[-1].lower() in self.pic_filename:
                gevent.spawn(self.img_load, img_url.groupdict()['title'], pic_src).join()  # join图片下载协程
            else:
                continue

    def img_load(self, pic_title, pic_url):
        try:
            print('img_dl', pic_url)
            pic = requests.request('GET', pic_url, timeout=5).content
            with open('{}{}.{}'.format(self.path, pic_title, pic_url.split('.')[-1]), 'wb') as f:
                f.write(pic)
        except Exception as e:
            print(e)

    def start(self):
        self.path_check()
        gevent.joinall([gevent.spawn(self.page_load, url) for url in self.page_gen])  # join所有页面


if __name__ == '__main__':
    LaifudaoSpider(1, 30, 'E:\\LaifudaoSpider\\').start()
