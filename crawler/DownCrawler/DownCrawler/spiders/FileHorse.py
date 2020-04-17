# -*- coding: utf-8 -*-

# Giovanni Bertao
# UNICAMP 2018
# Crawler used to download the most popular softwares from FileHorse

import scrapy                                   # Dig new pages
from DownCrawler.items import DowncrawlerItem   # Save item
import os                                       # Path configuration

class FilehorseSpider(scrapy.Spider):

    # Spider variables
    name = 'FileHorse'
    allowed_domains = ['www.filehorse.com']
    start_urls = ['http://www.filehorse.com/popular']
    base = 'http://www.filehorse.com/popular'

    # First parse every most popular software page
    def parse(self, response):
        for i in range(1, 6):
            if i == 1:
                url = self.base
            else:
                url = self.base+'/page-'+str(i)

            request = scrapy.Request(url, callback = self.parse_page, dont_filter = True, meta={'page':i})

            yield request

    # For each MPS page, parse every software download page
    def parse_page(self, response):
        urls = response.css("div[class='short_description'] h3 a::attr(href)").extract()
        rank = 10*(response.meta['page'] - 1) + 1

        for url in urls:

            url = url.encode("utf-8")
            request = scrapy.Request(url, callback = self.parse_sw, dont_filter = True, meta = {'rank':rank})
        
            rank+=1

            yield request

    # From download page, parse the download link page
    def parse_sw(self, response):
        url = response.css("div[class='main_down_link'] a::attr(href)").extract_first()
        name = response.css("div [itemprop='name'] a::text").extract_first().encode("utf-8")

        meta = response.meta
        meta['name'] = name

        if url != None:
            url = url.encode("utf-8")
            request = scrapy.Request(url, callback = self.parse_download, dont_filter = True, meta=meta)

            yield request

    # From download link page, parse the download link
    def parse_download(self, response):
        file_urls = response.xpath('//a[contains(@id,"download_url")]/@href').get().encode("utf-8")

        if file_urls != None:

            item = DowncrawlerItem()
            item['file_urls'] = [file_urls]
            item['name'] = response.meta['name'].encode("utf-8")
            item['path'] = os.path.join(self.settings['FILES_STORE'],"FileHorse")
            item['site'] = 'FileHorse'
            item['rank'] = response.meta['rank']

            yield item
