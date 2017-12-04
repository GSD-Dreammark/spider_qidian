import scrapy
import os
from bson.objectid import ObjectId
from scrapy.http import Request
from time import sleep
from qidianNovel.spiders.connectionSQL import getredis,getMongodb
# 把起点首页的所有列表,起点是最后两页没有下一页（此处当做一页）
status_flag=0
class spider_detail_novel(scrapy.Spider):
    name = "spider_detail_novel" #要调用的名字
    allowed_domains = ["qidian.com"] #分一个域
    start_urls = []
    dict = {}
    red = getredis()
    mongodb=getMongodb('novel','novels')
    def __init__(self):
        urls = self.red.lrange('all_novel_href', 0,-1)
        for url in urls:
            url = str(url, encoding="utf-8")
            url = url.split(',')
            spider_detail_novel.start_urls.append(url[1])
            spider_detail_novel.dict[url[1]] = url[0]
    #每爬完一个网页会回调parse方法
    def parse(self, response):
        global status_flag
        id = self.dict[response.url]
        Pid=(ObjectId(id))
        detail_messages=response.xpath('//div[@class="book-info "]')
        # 爬取详细信息
        for detail_message in detail_messages:
            author=detail_message.select('//h1/span/a/text()').extract()[0]
            status=detail_message.select('p/span/text()').extract()[0]
            if status=="连载":
                status_flag=0
            else:
                status_flag=1
            # 更新mongodb
            self.mongodb.update({"_id": Pid}, {"$set": {'author': author, 'status': status_flag}})
            novel_href ="https:"+ detail_message.select('p/a/@href').extract()[2]
            # 爬取小说
            request=Request(novel_href,callback=lambda response,id=id,status_flag=status_flag:self.spider_one_novel(response,id,status_flag))
            yield  request
    def spider_one_novel(self,response,id,status_flag):
        chapter_mongodb = getMongodb('novel', 'chapters')
        chapter=response.xpath('//h3[@class="j_chapterName"]/text()').extract()[0]
        print('********处理内容*******')
        contents = response.xpath('//div[@class="read-content j_readContent"]/p/text()').extract()
        novel_names = response.xpath('//div[@class="book-cover-wrap"]/h1/text()').extract()
        novel_name=response.xpath('//div[@class="crumbs-nav"]/a[@class="act"]/text()').extract()[0]
        if len(novel_names)!=0:
            os.makedirs('D:/all_novels/%s' %novel_names[0])
        else:
            pass
        f = open('D:/all_novels/%s/%s.html' % (novel_name,chapter), 'w', encoding='utf-8');
        file_path='D:/all_novels/%s/%s.html' % (novel_name,chapter)
        # 存入mongodb中
        chapter_mongodb.insert({chapter: file_path, 'pid': id})
        for content in contents:
            f.write(content)
            f.write('<br>')
        f.close()
        print('+++++++++++++++++++++')
        next_chapter = "https:"+response.xpath('//a[@id="j_chapterNext"]/@href').extract()[0]
        if next_chapter.find('lastpage')>0:
            if status_flag==0:
                self.red.lpush('serialize_list',id+','+response.url)
            return None
        print('+++++++++++++++++++++')
        request=Request(next_chapter,callback=lambda response,id=id,status_flag=status_flag:self.spider_one_novel(response,id,status_flag))
        yield request



