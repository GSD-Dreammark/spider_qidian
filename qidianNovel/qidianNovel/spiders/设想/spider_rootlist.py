import scrapy
from qidianNovel.spiders.connectionSQL import getredis,getMongodb
# 把起点首页的第一层列表存到数据库里
class spider_rootlist(scrapy.Spider):
    name = "spider_rootlist" #要调用的名字
    allowed_domains = ["qidian.com"] #分一个域
    start_urls = [#所有要爬路径
        "https://www.qidian.com/all?orderId=&page=1&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0"
    ]
    #每爬完一个网页会回调parse方法
    def parse(self, response):
        red = getredis()
        bcollection =getMongodb()
        hx=response.xpath('//div[@class="work-filter type-filter"]/ul/li/a|//div[@class="work-filter type-filter"]/ul/li/a')
        for i in range(1,len(hx)):
            print(hx[i].select("@href").extract()[0])  # 取长度
            print(hx[i].select("text()").extract()[0])  # 取长度str(hx[i].select("@href").extract()[0])
            id = bcollection.insert({'list_name': str(hx[i].select("text()").extract()[0])})
            red.lpush('novel_list', str(id) + "," + "https:"+str(hx[i].select("@href").extract()[0]))


