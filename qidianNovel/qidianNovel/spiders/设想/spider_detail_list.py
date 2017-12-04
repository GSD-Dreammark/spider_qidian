import scrapy
from qidianNovel.spiders.connectionSQL import getredis,getMongodb
# 把起点首页的第二层列表存到数据库里
class spider_detail_list(scrapy.Spider):
    name = "spider_detail_list" #要调用的名字
    allowed_domains = ["qidian.com"] #分一个域
    red=getredis()
    urls=red.lrange('novel_list',0,-1)
    start_urls = []
    ids=[]# 方法二
    dict={}# 方法一
    for url in urls:
        url = str(url, encoding="utf-8")
        url = url.split(',')
        start_urls.append(url[1])
        # ids.append(url[0]) # 方法二
        dict[url[1]]=url[0] # 方法一
    #每爬完一个网页会回调parse方法
    def parse(self, response):
        # 方法一：由于url是线程故无法判断id 是不是对应的url
        Pid=self.dict[response.url]
        bcollection =getMongodb()
        links = response.xpath('//div[@class="sub-type"]/dl[@class=""]/dd/a')
        for link in links:
            print("***************")
            print(Pid)
            print(link.select("text()").extract()[0])
            print(link.select('@href').extract()[0])
            print("***************")
            id = bcollection.insert({'list_child_name': link.select("text()").extract()[0], 'pid': Pid})
            self.red.lpush('bnovel_all_list', str(id) + "," + "https:" + link.select('@href').extract()[0])
        # 方法二：
        # response.url 获取当前的url
        # bcollection = getMongodb()
        # for url in self.urls:
        #     url = str(url, encoding="utf-8")
        #     url = url.split(',')
        #     if url[1]==response.url:
        #         links = response.xpath('//div[@class="sub-type"]/dl[@class=""]/dd/a')
        #         for link in links:
        #             print("***************")
        #             print(url[0])
        #             print(link.select("text()").extract()[0])
        #             print(link.select('@href').extract()[0])
        #             print("***************")
        #             id = bcollection.insert({'list_child_name': link.select("text()").extract()[0], 'pid': url[0]})
        #             self.red.lpush('bnovel_all_list', str(id) + "," + "https:" + link.select('@href').extract()[0])



