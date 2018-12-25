import aiohttp
import asyncio
import os
import re

loop = asyncio.get_event_loop()
page_regex = re.compile(r'<img alt="(?P<title>[^"]+)" src="(?P<src>http://down[0-9].laifudao.com/tupian/\d*.\w{3,4})"')


async def page_load(url, pic_filename, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            try:
                response = await asyncio.wait_for(response.read(), timeout=5)
            except asyncio.TimeoutError:
                return

    result = page_regex.finditer(response.decode('utf-8'))
    img_obj = {}  # title:url
    for img_url in result:
        pic_src = img_url.groupdict()['src']
        if pic_src.split('.')[-1].lower() in pic_filename:
            img_obj[img_url.groupdict()['title']] = pic_src
            # loop.create_task(img_load(path, img_url.groupdict()['title'], pic_src))
            # await img_load(path, img_url.groupdict()['title'], pic_src)
    await asyncio.gather(*[img_load(path, t, u) for t, u in img_obj.items()])


async def img_load(path, pic_title, pic_url):
    try:
        print('img_dl', pic_url)  # not safe
        async with aiohttp.ClientSession() as session:
            async with session.get(url=pic_url) as response:
                try:
                    pic = await asyncio.wait_for(response.read(), timeout=5)
                except asyncio.TimeoutError:
                    return
        with open('{}{}.{}'.format(path, pic_title, pic_url.split('.')[-1]), 'wb') as f:
            f.write(pic)
    except Exception as e:
        print(e)


class LaifudaoSpider:
    url_head, url_tail = 'http://www.laifudao.com/index_', '.htm'
    pic_filename = ('jpg', 'gif', 'jpeg', 'png', 'bmp')

    def __init__(self, start, end, path):
        self.start_page, self.end_page = start, end
        self.page_gen = self.page_add()
        self.path = path
        self.path_check()

    def page_add(self):
        for page_num in range(self.start_page, self.end_page + 1):
            yield self.url_head + str(page_num) + self.url_tail

    def path_check(self):
        if os.path.exists(self.path) is False:
            os.makedirs(self.path)
            print('mkdir ', self.path)

    def start(self):
        tasks = [page_load(url, self.pic_filename, self.path) for url in self.page_gen]
        loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == '__main__':
    import utils

    with utils.my_timeit():
        LaifudaoSpider(1, 30, 'E:\\LaifudaoSpider\\').start()
