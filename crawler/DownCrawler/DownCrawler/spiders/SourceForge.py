# -*- coding: utf-8 -*-

# Giovanni Bertao
# UNICAMP 2018
# Crawler that downloads the top 100 most popular 
# softwares from Source Forge

import scrapy                                   # Dig new pages
from DownCrawler.items import DowncrawlerItem   # Save item
import os                                       # Path configuration
import urllib2

class SourceforgeSpider(scrapy.Spider):

    # Spiders variables
    name = 'SourceForge'
    allowed_domains = ['sourceforge.net/']
    start_urls = ['https://sourceforge.net/directory/os:windows/']
    base = 'https://sourceforge.net/directory/os:windows/'
    projects = 'https://sourceforge.net'

    # First, parse the top downloads page
    def parse(self, response):
        for i in range(1,4):
            if i == 1:
                url = self.base
            else:
                url = self.base+'?page='+str(i)

            request = scrapy.Request(url, callback = self.parse_page, dont_filter = True, meta={'page':i})

            yield request

    # For each page, parse the software page
    def parse_page(self, response):
        urls = response.css("[class='button green hollow see-project']::attr(href)").extract()
        rank = 25*(response.meta['page']-1)+1

        for suffix in urls:
            url = self.projects + suffix
            request = scrapy.Request(url, callback = self.parse_sw, dont_filter = True, meta={'rank':rank})
            rank+=1

            yield request

    # For each software page, parse the download link and software name
    def parse_sw(self, response):
        suffix = response.css("div[class='buttons'] a[class='button download big-text green ']::attr(href)").extract_first()
        name = response.css("h1[itemprop='name']::text").extract_first().encode("utf-8")

        meta = response.meta
        meta['name'] = name
        if suffix:
            url = self.projects+suffix

            request = scrapy.Request(url, callback = self.parse_download, dont_filter = True, meta=meta)

            yield request        

    def parse_download(self, response):     

        req = urllib2.Request(response.url)
        aux = urllib2.urlopen(req)

        item = DowncrawlerItem()
        item['file_urls'] = [aux.url]
        item['name'] = response.meta['name'].encode("utf-8")
        item['path'] = os.path.join(self.settings['FILES_STORE'],"SourceForge")
        item['site'] = 'Source Forge'
        item['rank'] = response.meta['rank']
        
        yield item
