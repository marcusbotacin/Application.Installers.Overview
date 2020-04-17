# -*- coding: utf-8 -*-

# Giovanni Bertao
# UNICAMP 2018
# Spider used to crawl download.Cnet.com and download every
# software in 10 pages of popular softwares

import scrapy                                   # Dig new pages
from DownCrawler.items import DowncrawlerItem   # Save item
import os                                       # Path configuration

class CnetSpider(scrapy.Spider):

    # Spider Variables
    name = 'Cnet'
    allowed_domains = ['https://download.cnet.com/']
    start_urls = ['https://download.cnet.com/s/software/windows/?sort=most-popular/']
    page_url = 'https://download.cnet.com/s/software/windows/?sort=most-popular&page'
    download_url = 'https://download.cnet.com'

    # First parser, parse the most popular pages
    def parse(self, response):
        for page in range(1,11):
            if page == 1:
                url = self.page_url
            else:
                url = self.page_url+"="+str(page)

            request = scrapy.Request(url, callback = self.parse_page, dont_filter = True, meta={'page':page})

            yield request

    # For each MPP page, parse the software page
    def parse_page(self, response):
        urls = response.css("div[id='search-results'] a::attr(href)").extract()[0:10]
        rank = 10*(response.meta['page']-1)+1

        for url in urls:

            url = url.encode("utf-8")
            request = scrapy.Request(self.download_url+url, callback = self.parse_sw, dont_filter = True, meta={'rank':rank})

            rank+=1

            yield request

    # Parse the download link from the software page
    def parse_sw(self, response):

        if response.css("span#download-now-btn-text.dln-cta").get().split(">")[1].split("<")[0].encode("utf-8") == 'Download Now':
            url = response.css("[class='dln-a']::attr(href)").extract_first().encode("utf-8")
            name = response.css("h1.show_desktop").get().split(">")[2].split("<")[0].encode("utf-8")

            response.meta['name'] = name
                
            request = scrapy.Request(url, callback = self.parse_item, dont_filter = True, meta=response.meta)

            yield request

    def parse_item(self, response):

        url = response.css("[class='download-standby']").extract_first().split("href=")[1].split(">")[0].encode("utf-8").strip('"')
        if 'amp;' in url:
            url = url.replace('amp;','')

        item = DowncrawlerItem()
        item['file_urls'] = [url]
        item['name'] = response.meta['name']
        item['path'] = os.path.join(self.settings['FILES_STORE'],"Cnet")
        item['site'] = "Cnet"
        item['rank'] = response.meta['rank']
            
        yield item
