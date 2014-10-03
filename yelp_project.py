from bs4 import BeautifulSoup
import urllib2
import re
import html5lib
import os
import time
import random
import csv
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('MacOSX')


review_url = 'http://www.yelp.com/biz/gordo-taqueria-berkeley?start='
page_no = 0
more = True
rest = {review_url:{}}

while page_no < 40:
    request = urllib2.Request(review_url + str(page_no))
    try:
        page = urllib2.urlopen(request)
    except:
        more = False

    content = page.read()
    soup = BeautifulSoup(content, 'html5lib')

    more_test = soup.find_all('h3', text = True)
    for i in more_test:
        if ''.join(i.findAll(text=True))[0:6] == 'Whoops':
            more = False
            break
    #print soup.prettify()

    #<i class="star-img stars_4" title="4.0 star rating">

    if more:
        results = soup.find_all('meta',{'itemprop' : re.compile('ratingValue')})[1:]
        reviewers_find = soup.find_all('a',{'href':re.compile('/user_details\?userid\=[a-zA-Z0-9_]+')})[7:]
        rev_class = soup.find_all('strong',{'class':re.compile(r'review')})
        authors = soup.find_all('meta',{'itemprop':re.compile(r'author')})
        reviewers = []
        for i in range(len(reviewers_find)):
            if reviewers_find[i].get('href') != reviewers_find[i-1].get('href'):
                reviewers.append(reviewers_find[i].get('href'))

        for i in range(len(results)):
            try:
                print 'This restaurant\'s review:'
                print results[i].get('content') + ' star rating'
                print authors[i].get('content')
                print reviewers[i]
                current = reviewers[i]
                author = authors[i].get('content')
                reviewer_url = 'http://www.yelp.com' + str(reviewers[i])[0:13] + '_reviews_self' + str(reviewers[i])[13:]
                rest[review_url][reviewers[i]] = {}
                rest[review_url][reviewers[i]]['Name'] = authors[i].get('content')
                rest[review_url][reviewers[i]]['Score'] = float(results[i].get('content'))
                rest[review_url][reviewers[i]]['url'] = reviewer_url
                rest[review_url][reviewers[i]]['Reviews'] = []
            except:
                continue


            print reviewer_url
            print 'All other reviews by this reviewer'
            inner_more = True
            inner_page_no = 0
            while inner_more:
                inner_request = urllib2.Request(reviewer_url + '&rec_pagestart=' + str(inner_page_no))
                inner_page = urllib2.urlopen(inner_request)
                inner_content = inner_page.read()
                inner_soup = BeautifulSoup(inner_content, 'html5lib')
                inner_more_test = inner_soup.find_all('div', {'id':re.compile(r'empty')})
                for i in inner_more_test:
                    if i.get('id') == 'empty_reviews':
                        inner_more = False
                if inner_more:
                    rev_res = inner_soup.find_all('i',{'class' : re.compile(r'star')})
                    for res in rev_res[:-1]:
                        try:
                            print str(res.get('title'))[0:3]
                            rest[review_url][current]['Reviews'].append(float(str(res.get('title'))[0:3]))
                        except ValueError:
                            continue
                inner_page_no += 10
            fig = plt.figure()
            plt.hist(rest[review_url][current]['Reviews'])
            plt.savefig('/Users/scottkellert/Documents/YELP/'+ str(len(rest[review_url][current]['Reviews'])) + '_' + str(author)+'.pdf', format='pdf')
            print '##########################################################'


    page_no += 40

