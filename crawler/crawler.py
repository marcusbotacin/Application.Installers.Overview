# -*- coding: utf-8 -*-

# Giovanni Bertao
# UNICAMP 2018
# Crawler class used to run spiders in a child process
# Allows modularization

import subprocess           # Create child process
import os                   # Change to project dir, checks for valid dirs
import getopt               # Args parsing
import sys                  # Edith path
from threading import Timer # Timeout for child process
import re                   # Parse maximun size allowed string


# Crawler Class: Create a child process to run the spider
class Spider():
    def __init__(self, path, db, time, downpath, maxsize):
        self.spider_path = os.path.abspath(path)
        self.project_path = os.path.split(self.spider_path)[0]
        self.proc = None

        self.database = os.path.abspath(db)

        self.download = os.path.abspath(downpath)

        self.timeout = time

        self.maxsize = str(maxsize)

        if time > 0:
            self.timed = True
    
        else:
            self.timed = False

    def crawl(self):
        if os.path.exists(self.spider_path) and self.spider_path[-3:] == ".py" and os.path.exists(self.project_path):
            os.chdir(self.project_path)
            self.proc = subprocess.Popen(["/usr/bin/scrapy","runspider",self.spider_path,"-s","DB_PATH="+self.database,"-s","FILES_STORE="+self.download,"-s","DOWNLOAD_MAXSIZE="+self.maxsize])


            #After timeout, the child is killed
            if self.timed:
                timer = Timer(self.timeout, self.proc.kill)

            try:
                if self.timed:
                    timer.start()

                # Waits for child termination to proced
                stdout, stderr = self.proc.communicate()

            finally:
                if self.timed:
                    timer.cancel()
#Print usage
def usage():
    USE = """Crawler

Crawl programs from online repositories, each repository must have a spider at the
<spider directory>. It's possible to run just one spider with -s and feeding
the <spider path>. Every download will be stored under the <download path>
directory. After downloading a program, the program information will be stored
in a database located at <database>. It's possible to determine a maximum
download size with --maxsize <size>. For each spider crawling, a timeout can be
set with -t <timeout>.

Use: python crawler.py {-s <spider path> | -d <spider directory>}  --db <database> --download <download path> [-t <timeout>] [--maxsize <size>]

-s <spider path>: Will execute the spider in the path.
-d <spiders directory>: Will execute every spider on the directory.

-t <timeout>: seconds that each spider is alive. Default = until crawl is completed.

--db <database>: Database path.
--download <download path>: Will store every download
--maxsize <size>: Max size allowed to be download
  <size> format is 'XYB', read as 'X Y-byte', the default value is 1GB(1024MB)
"""
    print(USE)

# Run from shell
if __name__=="__main__":

    if len(sys.argv) <= 4:
        usage()
        sys.exit(1)

    # Parse args
    try:
        args, trash = getopt.getopt(sys.argv[1:],"s:t:d:",["db=","download=","maxsize=","help"])

    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)


    timeout = 0
    maxsize = '1GB'
    db = None
    spath = None
    dpath = None
    downpath = None

    for arg, value in args:
        if arg == "-s":
            spath = os.path.abspath(value)

        elif arg == "-t":
            timeout = float(value)

        elif arg == "--db":
            db = os.path.abspath(value)

        elif arg == "-d":
            dpath = os.path.abspath(value)

        elif arg == "--download":
            downpath = os.path.abspath(value)

        elif arg == "--maxsize":
            maxsize = value

        elif arg == "--help":
            usage()
            sys.exit(1)

        else:
            usage()
            sys.exit(1)

    # Checking args standards
    # Download size
    if re.findall(r"^(\d+|\d+\.\d+)[KMGT]B$",maxsize):
        num = maxsize[0:-2]
        unit = maxsize[-2]
        mult = 1024
        
        if unit == 'K':
            mult = mult **1

        elif unit == 'M':
            mult = mult**2

        elif unit == 'G':
            mult = mult**3

        elif unit == 'T':
            mult = mult**4

        else:
            print("Incorrect size unit")
            usage()
            sys.exit(1)

        maxsize = int(num)*mult+1

    else:
        print("Incorrect size")
        usage()
        sys.exit(1)
        
    # Download destination path
    if downpath == None:
        print("Missing Download Destination Folder")
        usage()
        sys.exit(1)

    # Database file
    if db == None:
        print("Missing Database File")
        usage()
        sys.exit(1)

    # Execute every spider in a directory or just one spider
    if dpath != None:

        if not os.path.isdir(dpath):
            print("Invalid Directory")
            usage()
            sys.exit(1)

        else:
            spiders = []
            for files in os.listdir(dpath):
                if files[-3:] == ".py" and files != "__init__.py":
                    spiders.append(os.path.join(dpath,files))


            for item in spiders:
                spider = Spider(item, db, timeout, downpath, maxsize)
                spider.crawl()
            
    else:

        if spath == None:
            print("Missing Spider")
            usage()
            sys.exit(1)
        
        else:
            spider = Spider(spath, db, timeout, downpath, maxsize)
            spider.crawl()
