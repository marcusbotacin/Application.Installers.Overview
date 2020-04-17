# -*- coding: utf-8 -*-

# Giovanni Bertao
# UNICAMP 2018
# Item class file

import scrapy


class DowncrawlerItem(scrapy.Item):
    # field used by File Pipeline Class
    file_urls = scrapy.Field()      # URLs used to download the software at file's pipeline stage
    files = scrapy.Field()

    name = scrapy.Field()           # Store file name, used to produce the local path
    site = scrapy.Field()           # Site used to download
    rank = scrapy.Field()           # Rank as apeard in a site

    download_date = scrapy.Field()  # Completed in pipeline stage
    md5 = scrapy.Field()            # Completed in pipeline stage
    path = scrapy.Field()           # Temporary store incomplete path. Full path at pipeline stage
