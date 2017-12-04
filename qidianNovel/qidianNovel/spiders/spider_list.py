import scrapy
from bson.objectid import ObjectId
from scrapy.http import Request
from qidianNovel.spiders.connectionSQL import getredis,getMongodb
# 把起点首页的所有列表
class spider_list(scrapy.Spider):
    name = "spider_list" #要调用的名字
    allowed_domains = ["qidian.com"] #分一个域
    start_urls = [#所有要爬路径
        "https://www.qidian.com/all?orderId=&page=1&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0"
    ]
    #每爬完一个网页会回调parse方法
    def parse(self, response):
        hx=response.xpath('//div[@class="work-filter type-filter"]/ul/li/a|//div[@class="work-filter type-filter"]/ul/li/a')
        for i in range(1,len(hx)):
            print(hx[i].select("text()").extract()[0])  # 取长度
            Pid=self.insertMongodb(hx[i].select("text()").extract()[0],None)
            url="https:"+hx[i].select("@href").extract()[0]
            print(url)
            request=Request(url,callback=lambda response,Pid=str(Pid):self.detail_list(response,Pid))
            yield request
    def detail_list(self,response,Pid):
        links = response.xpath('//div[@class="sub-type"]/dl[@class=""]/dd/a')
        pid=ObjectId(Pid)
        for link in links:
            print("***************")
            print(link.select("text()").extract()[0])
            print(link.select('@href').extract()[0])
            print("***************")
            cid=self.insertMongodb(link.select("text()").extract()[0],pid)
            href="https:" + link.select('@href').extract()[0]
            self.pushRedis(pid,cid,href)
    def insertMongodb(self,className,pid):
        bcollection = getMongodb('novel', 'boy_list')
        id = bcollection.insert({'list_name': className, 'pid': pid})
        return id
    def pushRedis(self,pid,cid,href):
        red = getredis()
        href="%s,%s,%s" %(pid,cid,href)
        red.lpush('bnovel_all_list',href)


