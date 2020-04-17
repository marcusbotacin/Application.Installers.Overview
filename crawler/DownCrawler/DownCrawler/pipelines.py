# -*- coding: utf-8 -*-

# Giovanni Bertao
# UNICAMP 2018
# Pipelines file

import scrapy
from scrapy.pipelines.files import FilesPipeline    # Used to create a new file pipeline class
from scrapy.exceptions import DropItem
import os                                           # Storage path
from scrapy.exporters import JsonItemExporter       # Save items to json file
import datetime                                     # Calculate download date
import subprocess                                   # Create database
import sqlite3                                      # Populate database

class DowncrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

# Pipeline to download the file
class MyFilesPipeline(FilesPipeline):
    def file_path(self, request, response = None, info=None):
        path = request.meta['name']
        path = path.replace(" ","_")
        path = path.replace("/","")
        return os.path.join(path,path+'.exe')

    def get_media_requests(self, item, info):
        yield scrapy.Request(url = item['file_urls'][0], meta = {'name':item['name']})

# Pipeline to retrieve the file path
class PathPipeline(object):
    def process_item(self, item, spider):
        item['path'] = os.path.join(item['path'],item['files'][0]['path'])
        
        return item

# Pipeline to calculate the MD5
class MD5Pipeline(object):
    def process_item(self, item, spider):
        item['md5'] = item['files'][0]['checksum']
        
        return item

# Pipeline to store download date
class DatePipeline(object):
    def process_item(self, item, spider):
        item['download_date'] = str(datetime.datetime.now())

        return item
        
# Pipeline to save item in json file
class JsonOutputPipeline(object):
    def __init__(self):
        self.file = open("Downloads.json","w")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False,indent=2)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)

        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

# Database Pipeline
class DBPipeline(object):
    # settings = database path
    def __init__(self, settings):
        self.DB_PATH = settings

    # Retrieve database path from settings.py file
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings.get("DB_PATH")
        return cls(settings)
        
    # For each downloaded item, insert it's data on database
    def process_item(self, item, spider):
        sql = "INSERT INTO Downloads(DATE, MD5, SITE, NAME, RANK) VALUES(?, ?, ?, ?, ?)"
        date = item['download_date']
        md5 = item['md5']
        site = item['site']
        rank = item['rank']
        name = item['name']

        self.cur.execute(sql, (date, md5, site, name, rank))

        return item

    # For each spider, stabilishes a connection to the database
    def open_spider(self, spider):
        # Verify for valid path
        if not os.path.exists(os.path.abspath(self.DB_PATH)):
            self.CreateDB()

        self.con = sqlite3.connect(self.DB_PATH)
        self.cur = self.con.cursor()
        self.cur.execute("PRAGMA TEMP_STORE = MEMORY")
        self.cur.execute("PRAGMA JOURNAL_MODE = MEMORY")
        self.cur.execute("PRAGMA SYNCHRONOUS = OFF")

    # When an spider finishes
    def close_spider(self, spider):
        self.con.commit()
        self.con.close()

    # When the database file is missing, create one using the sql file on DB folder
    def CreateDB(self):
        SQL_PATH = self.DB_PATH[:-3]+".sql"
        sql_file = open(SQL_PATH,"r")
        proc = subprocess.Popen(["sqlite3", self.DB_PATH], stdin = sql_file)
        proc.communicate()
        sql_file.close()
