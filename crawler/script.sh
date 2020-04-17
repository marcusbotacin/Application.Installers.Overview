#!/bin/bash

# UNICAMP 2019
# Giovanni Bertao
# Script used in cron to schedule every crawler
# crawler.py has a --help argument

export PATH=$PATH:$PWD
export DIR='/home/user/IC/crawlerNovo'
cd $DIR

python3 $DIR/crawler.py -d $DIR/DownCrawler/DownCrawler/spiders/ --db $DIR/DB/crawler.db --download $DIR/Downloads/$(date +%y%m%d) 

#--maxsize 0MB

# -d 					Run every crawler at the spiders directory
# --db 				Database path
# --download 	Is the parent download directory, every file will be its child, uses date command
# --maxsize		Only download files that are less or equal the maxsize(20MB)
