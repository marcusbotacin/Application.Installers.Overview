# -*- coding: utf-8 -*-

# Giovanni Bertao
# UNICAMP 2018
# Spider that downloads the 100 most popular software from FileHippo

import scrapy                                   # Dig new pages
from DownCrawler.items import DowncrawlerItem   # Save item
import os                                       # Path configuration

class FilehippoSpider(scrapy.Spider):

    # Spider properties and variables
    name = 'FileHippo'
    allowed_domains = ['filehippo.com/']
    start_urls = ['https://filehippo.com/popular/']
    base_url = 'https://filehippo.com/popular/'

    # First, parse the 10 most popular software pages
    def parse(self, response):
        for page in range(1,11):
            # Producing URL
            if page == 1:
                next_req = self.base_url
            else:
                next_req = self.base_url+str(page)

            request = scrapy.Request(next_req, callback = self.parse_page, dont_filter=True, meta={'page':page})   

            yield request

    # For each popular page crawl the software download page
    def parse_page(self, response):
        programs_url = response.css("[class='card-program']::attr(href)").getall()
        rank = 10*(response.meta['page']-1)+1
        
        for url in programs_url:
            url = url.encode("utf-8")
            request = scrapy.Request(url, callback = self.parse_download, dont_filter=True, meta={'rank':rank})

            rank+=1

            yield request

    # For each download page crawl the intermediate download link and software name
    def parse_download(self, response):
        urls = response.xpath("//a[@class='program-button program-button--download program-actions-header__button program-button-download js-program-button-download']/@href").extract_first().encode("utf-8")
        name = response.css("span.program-header__name").get().encode("utf-8").split(">")[1].split("<")[0]

        if name == None:
            name = response.css('title::text').get().split(" ")[1].encode("utf-8")

        meta = response.meta
        meta['name'] = name

        
        request = scrapy.Request(urls, callback = self.parse_file, dont_filter=True, meta=meta)
                
        yield request

    # For each intermediate download link crawl the final link to download the file
    def parse_file(self, response):

        if 'post_download' not in response.url:
            response.replace(url = response.url+'post_download')

        name_1 = response.meta['name'].encode("utf-8")
        rank_1 = response.meta['rank']
        aux = response.text

        if 'data-qa-download-url' in aux:
            a = aux.split("data-qa-download-url=")[1].split(">")[0].strip('"').replace('amp;','')
            response = scrapy.http.TextResponse(url=a)

            if '.rar' not in response.url:
                item = DowncrawlerItem()
                item['file_urls'] = [response.url]
                item['name'] = name_1
                item['path'] = os.path.join(self.settings['FILES_STORE'],"FileHippo")
                item['site'] = 'FileHippo'
                item['rank'] = rank_1

                yield item