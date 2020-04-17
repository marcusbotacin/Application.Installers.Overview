# -*- coding: utf-8 -*-

# Giovanni Bertao
# UNICAMP 2018
# Spider that downloads the top 3 softwares from each category of Softpedia

import scrapy                                   # Dig new pages
from DownCrawler.items import DowncrawlerItem   # Save item
import os                                       # Path configuration
from selenium import webdriver
import time


class SoftpediaSpider(scrapy.Spider):

    # Spider properties and variables
    name = 'Softpedia'
    start_urls = ['https://win.softpedia.com/']

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    global driver
    driver = webdriver.Chrome(chrome_options=options)


    # First parse all categories pages
    def parse(self, response):

        categories = response.css("[class='ellip'] a::attr(href)").extract()

        for next_req in categories:
            next_req = next_req.encode("utf-8")
            request = scrapy.Request(next_req, callback=self.parse_category, dont_filter = True)

            yield request

    # At each category page, crawl the top 3 softwares
    def parse_category(self, response):
        program = response.css("[class='ln'] a::attr(href)").extract()
        cat = response.url.split("/")[-2]
        for i in range(3):
            next_req = program[i].encode("utf-8")
            request = scrapy.Request(next_req, callback = self.parse_idnum, dont_filter = True, meta={'rank':cat+"-"+str(i+1)})
            
            yield request

    # For each software, crawl their download page
    def parse_idnum(self, response):

        site = response.url+'#download'

        driver.get(site)
        time.sleep(1)
        aux = driver.page_source
        time.sleep(1)
        sel = scrapy.Selector(text=aux)

        url = sel.xpath('//a[contains(@href,"/dyn-postdownload.php/")]/@href').get()
        if url != None:
            request = scrapy.Request(url, callback = self.parse_file, dont_filter = True, meta=response.meta)
        
            yield request


    #Process a pipeline item
    def parse_file(self, response):
        name = response.css('title::text').get().split(" ")[0].encode("utf-8")
        file_urls = response.xpath('//a[contains(@title,"Click to start it manually")]/@href').get().encode("utf-8")

        item = DowncrawlerItem()
        item['file_urls'] = [file_urls]
        item['name'] = name.encode("utf-8")
        item['path'] = os.path.join(self.settings['FILES_STORE'],"Softpedia")
        item['site'] = 'Softpedia'
        item['rank'] = response.meta['rank']

        yield item