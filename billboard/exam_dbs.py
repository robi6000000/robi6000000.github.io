# # import scrapy
# import csv

# class SpiderWiki(scrapy.Spider):
#     name = 'spiderWiki'
#     start_urls = ['https://en.wikipedia.org/wiki/Lists_of_Billboard_number-one_singles']

#     def parse(self, response):
#         pre_hot_100_era = response.xpath("//span[@id='Pre-Hot_100_era']/following::table[1]//a")
#         for link in pre_hot_100_era:
#             year = link.xpath("text()").get()
#             url = link.xpath("@href").get()
#             full_url = response.urljoin(url)
#             yield {'year': year, 'era': 'pre-hot100', "pre-2012": True, 'url': full_url}

#         hot_100_era = response.xpath("//span[@id='Hot_100_era']/following::table[1]//a")
#         for link in hot_100_era:
#             pre_2012 = False
#             year = link.xpath("text()").get()
#             if int(year) < 2012:
#                 pre_2012 = True
#             url = link.xpath("@href").get()
#             full_url = response.urljoin(url)
#             yield {'year': year, 'era': 'hot100', 'pre-2012': pre_2012, 'url': full_url}

# class SpiderBillboard(scrapy.Spider):
#     name = 'spiderBillboard'

#     def start_requests(self):
#         with open('billboard1.csv', 'r', newline='', encoding='utf-8') as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 yield scrapy.Request(url=row['url'], callback=self.parse, meta={'era': row['era'], 'pre-2012': row['pre-2012'], 'year': row['year']})

#     def parse(self, response):
#         if response.meta['pre-2012'] == 'True':
#             table = response.xpath("(//table[@class='wikitable'])[2]//tr")
#         else:
#             table = response.xpath("(//table[@class='wikitable plainrowheaders'])[1]//tr")
        

#         for song in table[1:]:
#             if response.meta['pre-2012'] == 'False':
#                 title = song.xpath("td[2]/a/text()").get() or song.xpath("td[2]/text()").get()
#                 artist = song.xpath("td[3]/a/text()").get() or song.xpath("td[3]//span/span/span/text()").get() or song.xpath("td[3]/text()").get()
#                 url = song.xpath("td[2]/a/@href").get() 
#                 full_url = response.urljoin(url) if url else ''
#             else:
#                 title = song.xpath("td[3]/a/text()").get() or song.xpath("td[3]/text()").get()
#                 artist = song.xpath("td[4]/a/text()").get() or song.xpath("td[4]/text()").get()
#                 url = song.xpath("td[3]/a/@href").get()
#                 full_url = response.urljoin(url) if url else ''
#             print(response.meta)
#             year = response.meta['year']
#             era = response.meta['era']
#             if title and artist:
#                 yield {'title': title.strip(), 'artist': artist.strip(), 'year': year, 'era': era, 'url': full_url.strip()}

# class SpiderSong(scrapy.Spider):
#     name = 'spiderSong'

#     def start_requests(self):
#         with open('billboardConsolidated.csv', 'r', newline='', encoding='utf-8') as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 if row['url']:
#                     yield scrapy.Request(url=row['url'], callback=self.parse, meta={'title': row['title'], 'artist': row['artist'], 'year':row['year'], 'count': row['count']})
#                 else:
#                     yield scrapy.Request(url='https://en.wikipedia.org/wiki/Lists_of_Billboard_number-one_singles', callback=self.parse, meta={'title': row['title'], 'artist': row['artist'], 'year':row['year'], 'count': row['count']})


#     def parse(self, response):
#         table = response.xpath("//table[@class='infobox vevent']//tr")
#         year = ''
#         genre = ''
#         length = ''

#         for row in table:
#             label = row.xpath("th[@class='infobox-label']/text()").get()
#             if not label:
#                 label = row.xpath("th[@class='infobox-label']/a/text()").get()
#             if label:
#                 label = label.strip()

#             if label == 'Released':
#                 year = row.xpath("td[@class='infobox-data plainlist']/text()").get()
#                 if year and not year.isdigit():
#                     year = row.xpath("td[@class='infobox-data plainlist']/a/text()").get()
#                 if year:
#                     year = year.strip()[-4:]
#                 else:
#                     year = response.meta['year']
                    
            
#             elif label == 'Genre' or label == 'Music genre':
#                 genre_elements = row.xpath("td[@class='infobox-data category hlist']/a/text()").getall()
#                 if genre_elements:
#                     genre = genre_elements[0]
#                 else:
#                     genre_elements = row.xpath("td[@class='infobox-data category hlist']/ul/li/a/text()").getall()
#                     if genre_elements:
#                         genre = genre_elements[0]

#             elif label == 'Length':
#                 mins = row.xpath("td[@class='infobox-data plainlist']/span[@class='duration']/span[@class='min']/text()").get()
#                 secs = row.xpath("td[@class='infobox-data plainlist']/span[@class='duration']/span[@class='s']/text()").get()
#                 if mins and secs:
#                     length = mins + ':' + secs

                

#         yield {
#             'title': response.meta['title'], 
#             'artist': response.meta['artist'],   
#             'count': response.meta['count'], 
#             'year of release': year, 
#             'genre': genre, 
#             'length': length
#         }


# create a db and table to which we output the first spider results

import sqlite3
import pandas as pd
from billboardProject.spiders.spiderWiki import SpiderWiki


def db():
    conn = sqlite3.connect('billboard.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS billboardYears (year TEXT, era TEXT, pre_2012 BOOLEAN, url TEXT)''')
    conn.commit()
    conn.close()

db()


