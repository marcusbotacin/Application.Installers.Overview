# -*- coding: utf-8 -*-
import pdb
import scrapy
from RepoCrawler.items import RepocrawlerItem

class FilehippotopSpider(scrapy.Spider):
    name = 'FileHippoTop'
    allowed_domains = ['filehippo.com/popular/']
    start_urls = ['http://filehippo.com/popular/']
    base_url = 'http://filehippo.com/popular/'

    def parse(self, response):
        for page in range(1,11):
            if page == 1:
                next_req = self.base_url
            else:
                next_req = self.base_url+str(page)

            request = scrapy.Request(next_req, callback = self.parse_page, dont_filter=True)   

            yield request

    def parse_page(self, response):
        programs = response.css("div [class = program-entry-header] h2::text").extract()
        for program in programs:
            item = RepocrawlerItem()
            item['rank'], item['program'] = program.encode("utf-8").split(". ")

            yield item
