import scrapy
from qidianNovel.spiders.connectionSQL import getredis,getMongodb
# 把起点每种类型的小说爬到库里
class spider_type_list(scrapy.Spider):
    name = "spider_type_list" #要调用的名字
    allowed_domains = ["qidian.com"] #分一个域
    start_urls = []
    red = getredis()
    urls = red.lrange('bnovel_all_list', 0, -1)
    dict={}
    for url in urls:
        url = str(url, encoding="utf-8")
        url = url.split(',')
        start_urls.append(url[1])
        dict[url[1]] = url[0]
    #每爬完一个网页会回调parse方法
    def parse(self, response):
        print("**********")
        links=response.xpath('//div[@class="book-mid-info"]/h4/a')
        for link in links:
            print(link.select("text()").extract()[0])
            print(link.select("@href").extract()[0])
        print("++++++++++++")


