import scrapy
from scrapy.http import Request
from time import sleep
from qidianNovel.spiders.connectionSQL import getredis,getMongodb
# 把起点首页的所有列表,起点是最后两页没有下一页（此处当做一页）
class spider_list_novel(scrapy.Spider):
    name = "spider_list_novel" #要调用的名字
    allowed_domains = ["qidian.com"] #分一个域
    start_urls = []
    dict = {}
    red = getredis()
    mongodb=getMongodb('novel','novels')
    def __init__(self):
        urls = self.red.lrange('bnovel_all_list', 0, -1)
        for url in urls:
            url = str(url, encoding="utf-8")
            url = url.split(',')
            spider_list_novel.start_urls.append(url[2])
            spider_list_novel.dict[url[2]] ={'classId':url[0],'listId':url[1],'sum':0}
            # break
    #每爬完一个网页会回调parse方法
    def parse(self, response):
        print(response.url)
        Pid = self.dict[response.url]
        Pid['sum']+=1
        print(Pid['sum'])
        if Pid['sum']>3:
            return
        links = response.xpath('//div[@class="book-mid-info"]/h4/a')
        for link in links:
            novel_name = link.select("text()").extract()[0]
            novel_id = self.mongodb.insert({'name': novel_name, 'total_list': Pid['classId'], 'list': Pid['listId']})
            href = link.select("@href").extract()[0]
            href = str(novel_id) + ',' + 'https:' + href
            print(href)
            self.red.lpush('all_novel_href',href)
        sleep(0.3)
        href=self.find_next(response)
        if href==None:
            f = open('file/%s.txt' % ("日志"), 'a', encoding='utf-8')
            f.write(response.url)
            f.write('++++++++++++++')
            f.close()
        else:
            href="https:"+href
            if href.find('javascript:;')<0:
                self.dict[href] = Pid
                request=Request(href,callback=self.parse)
                yield request
    def find_next(self,response):
        try:
            hrefs =response.xpath('//li[@class="lbf-pagination-item"]/a')
            i=len(hrefs)
            href=hrefs[i - 1].select("@href").extract()[0]
            return href
        except Exception as err:
            f = open('file/%s.txt' % ("日志"), 'a', encoding='utf-8')
            f.write(str(err)+':'+href)
            f.close()
            return None

