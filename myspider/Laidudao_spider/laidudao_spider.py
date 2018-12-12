import requests
import re
import os


class LaifudaoSpider:
    url_head, url_tail = 'http://www.laifudao.com/index_', '.htm'
    regex = re.compile(r'<img alt="(?P<title>[^"]+)" src="(?P<src>http://down[0-9].laifudao.com/tupian/\d*.\w{3,4})"')

    def __init__(self, start, end, path):
        self.start_page, self.end_page = start, end
        self.path = path

    def path_check(self):
        if os.path.exists(self.path) is False:
            os.makedirs(self.path)
            print('mkdir ', self.path)

    def page_gen(self):
        for page_num in range(self.start_page, self.end_page + 1):
            yield self.url_head + str(page_num) + self.url_tail

    def page_load(self):
        for url in self.page_gen():
            try:
                response = requests.request('GET', url, timeout=10).content.decode('utf-8')
            except Exception:
                try:
                    response = requests.request('GET', url, timeout=10).content.decode('utf-8')
                except Exception:
                    continue
            result = self.regex.finditer(response)
            for img_url in result:
                if img_url.groupdict().get('src'):
                    pic_src = img_url.groupdict()['src']
                    self.img_load(img_url.groupdict()['title'], pic_src)

    def img_load(self, pic_title, pic_url):
        print('img_dl', pic_url)
        try:
            pic = requests.request('GET', pic_url, timeout=5).content
            with open('{}{}.{}'.format(self.path, pic_title, pic_url.split('.')[-1]), 'wb') as f:
                f.write(pic)
        except Exception as e:
            print(e)

    def start(self):
        self.path_check()
        self.page_load()


if __name__ == '__main__':
    LaifudaoSpider(1, 30, 'E:\\LaifudaoSpider\\').start()
