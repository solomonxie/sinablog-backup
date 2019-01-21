# Python3
# ---coding:utf-8---

# ==== This project should be running in a python3 enviroment, preferred in Virtualenv. ====
#
# Author: Solomon Xie
# Email: solomonxiewise@gmail.com
# Project: Sina Blog Crawler
# Description: scrap my sina blogs and backup
#

import requests
import re
import os
import time
from random import random
from bs4 import BeautifulSoup

headers = {
    'host': "blog.sina.com.cn",
    'connection': "keep-alive",
    'cache-control': "max-age=0",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'referer': "http://blog.sina.com.cn/xiexiaobo",
    'accept-encoding': "gzip, deflate",
    'accept-language': "en,zh-CN;q=0.9,zh;q=0.8",
    'cookie': "blogAppAd_blog7articlelist=1; _s_loginuid=3376136144; blogAppAd_blog7article=1; SINAGLOBAL=59.63.206.199_1521607141.504874; Apache=59.63.206.199_1521607141.504876; UM_distinctid=1628d2c879f57f-0c6f9a6506fe8a-33697b04-13c680-1628d2c87a08af; U_TRS1=0000005d.32807f60.5ae7f5d4.ff208dcd; U_TRS2=0000005d.32897f60.5ae7f5d4.b9086e7f; SCF=Asv5GqTXeqjuhP0g-e1XJ6GLHH1n4K7tZUtyp0uk_WtP4j5SkA-viLsmy1Mkq8mXLmpyyMkftE2OFKYlnSwqU7o.; ULOGIN_IMG=tc-96bb0972f2217659ac50e99e5e0456853ce0; SessionID=o4s1fva13p96mn0c2ugm73va72; IDC_LOGIN=BJ%3A1526474766; _s_loginStatus=3376136144; __PicSessHandler=3984dc2d208e0cb75ff20540260158ef; SUB=_2AkMtoKWTdcPxrABSn_4Uz23jaIlH-jyedcxlAn7tJhMyAhh77lUzqSVutBF-XMTWIj9JiMV-5A-gN1S2vfPV8Cjm; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WFAmhX.sdQpzgJqsEYXAp0C5JpV2PyD9HvRIg8aqJv5MP2Vqcv_; UOR=video.sina.com.cn,news.video.sina.com.cn,; ULV=1526475491416:1:1:1:59.63.206.199_1521607141.504876:; SGUID=1526792852785_41569881; ArtiFSize=14; lxlrttp=1526753611; BLOG_TITLE=%E8%B0%A2%E8%8E%B1%E7%BA%B3%E7%9A%84%E5%8D%9A%E5%AE%A2; blogAppAd_blog7index=1; _s_loginuid=3376136144"
}

def main():
    #import pdb; pdb.set_trace()

    url = 'http://blog.sina.com.cn/s/articlelist_1253924794_0_1.html'
    path = '/Volumes/SD/Downloads/sinablog'
    sinablog = BlogSite(url, path)
    sinablog.download()


class BlogSite:
    def __init__(self, url, path):
        self.article_list_url = url
        self.article_urls = []
        self.path = path

        if os.path.exists(self.path+'/blog-lists.txt') is True:
            with open(self.path+'/blog-lists.txt', 'r') as f:
                self.article_urls = f.readlines()


    def fetch_article_list(self, url):
        """
        Fetch blog list page by page
        """
        print(url)

        r = requests.get(url, headers=headers, timeout=10)
        html = r.text
        time.sleep(1)

        if r.status_code is not 200:
            print('Server dinied. Status:[%s].'%r.status_code)
            return

        # local data test
        #with open('./dataset/sina-blog-list.html', 'r') as f:
        #    html = f.read()

        #print(html)

        soup = BeautifulSoup(html, 'html5lib')
        tags = soup.select('div[class=articleList] > div[class~=articleCell] > p > span[class=atc_title] > a')

        for t in tags:
            print('Appened: '+t['href'])
            self.article_urls.append(t['href'])

        # Get the url of next blog-list page
        nxpage = soup.select('div[class=SG_page] > ul > li[class=SG_pgnext] > a')
        if len(nxpage) > 0:
            #print ('Next list page: '+nxpage[0]['href'])
            self.fetch_article_list(nxpage[0]['href'])
        else:
            print('Have reached to the botom of blog lists.')


        # backup lists to local file
        with open(self.path+'/blog-lists.txt', 'w') as f:
            f.write('\n'.join(self.article_urls))


    def download(self):
        if len(self.article_urls) < 1:
            # Fetching online
            self.fetch_article_list(self.article_list_url)

        # Start fetching each blog page
        for url in self.article_urls:
            # Download articles
            blog = Article(url)
            filename = '%s/%d.MD' % (self.path, self.article_urls.index(url)+1)
            doc = '# %s \n@ %s \n[原文地址](%s) \n\n%s' %(blog.title, blog.time, blog.url, blog.content)
            with open(filename, 'w') as f:
                f.write(doc)
            #break


class Article:
    def __init__(self, url):
        self.url = url
        self.title = ''
        self.time = ''
        self.content = ''

        # start fetching blog 
        self.fetch_blog(self.url)


    def fetch_blog(self, url):
        print(url)

        r = requests.get(url, headers=headers, timeout=10)
        html = r.content

        if r.status_code is not 200:
            print('Server dinied. Status:[%s].'%r.status_code)
            return

        # local data test
        #with open('./dataset/sina-blog-content.html', 'r') as f:
        #    html = f.read()

        soup = BeautifulSoup(html, 'html5lib')

        tags = soup.select('div.articalTitle > h2')
        self.title = tags[0].get_text() if len(tags) > 0 else ''
        print(self.title)

        tags = soup.select('div.articalTitle > span[class~=time]')
        self.time = tags[0].get_text() if len(tags) > 0 else ''
        #print(self.time, type(self.time))

        tags = soup.select('div#sina_keyword_ad_area2')
        self.content = tags[0].get_text().strip('\n\t\r') if len(tags) > 0 else 'N/A'
        #print(self.content, type(self.content))

        # set random time gap before next run
        time.sleep(round(10*random(), 2))





if __name__ == "__main__":
    main()
