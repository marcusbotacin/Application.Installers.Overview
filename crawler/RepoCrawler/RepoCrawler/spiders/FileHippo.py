# -*- coding: utf-8 -*-
import pdb
import scrapy
from RepoCrawler.items import RepocrawlerItem

class FilehippoSpider(scrapy.Spider):
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
        programs_url = response.css("div [class = program-entry-header] a::attr(href)").extract()
        for url in programs_url:
            url = url.encode("utf-8")
            request = scrapy.Request(url, callback = self.parse_download, dont_filter=True)

            yield request

    def parse_download(self, response):
        file_url = response.xpath("//a[@class='program-header-download-link green button-link active long download-button']/@href").extract()
        item = RepocrawlerItem()
        item['file_url'] = file_url
        
        yield item
