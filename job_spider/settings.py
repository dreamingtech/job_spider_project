# -*- coding: utf-8 -*-
import logging
import os
# Scrapy settings for job_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'job_spider'

SPIDER_MODULES = ['job_spider.spiders']
NEWSPIDER_MODULE = 'job_spider.spiders'

# 默认的日志配置
DEFAULT_LOG_LEVEL = logging.INFO    # 默认等级
DEFAULT_LOG_FMT = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s'   # 默认日志格式
DEFUALT_LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'  # 默认时间格式
DEFAULT_LOG_FILENAME = 'log.log'    # 默认日志文件名称

# 代理池设置
# mogou: 1/s, xdaili: 1/5s
PROXY_API_LIST = [
    'http://piping.mogumiao.com/proxy/api/get_ip_al?appKey=3edd124e5381&count=1&expiryDate=0&format=1&newLine=2',
    'http://piping.mogumiao.com/proxy/api/get_ip_al?appKey=b9ed2f1d466c52&count=1&expiryDate=0&format=1&newLine=2',
    # '{"code":"3001","msg":"提取频繁请按照规定频率提取!"}'
    # '{"code":"0","msg":[{"port":"35379","ip":"117.60.2.113"}]}'
    'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=9b3e091022d73&orderno=YZ20FSf&returnType=2&count=1'
    # {"ERRORCODE":"10055","RESULT":"提取太频繁,请按规定频率提取!"}'
    # {"ERRORCODE":"0","RESULT":[{"port":"48448","ip":"115.203.196.254"}]}'
]

PROXY_REDIS_HOST = "localhost"
PROXY_REDIS_PORT = 6379
PROXY_REDIS_DB = 0

# 爬虫的爬取节点数
CRAWL_NODE_NUM = 1
# 启用的爬虫, 从代理api获取代理地址时, 添加到所有爬虫对应的redis key中
SPIDER_NAMES = (
    "boss",
    "job51",
    "lagou"
)

# mongodb 数据库设置
MONGO_URL = 'mongodb://127.0.0.1:27017'  # 配置MongoDB的URL
MONGO_ADDR = ['127.0.0.1:27017']  # mongodb数据库地址, 可以配置多个
MONGO_AUTH = None    # 数据库认证
MONGO_REPLICASET = None  # mongodb的备份
MOTOR_AUTH = None

# mysql 数据库设置
MYSQL_IP = '10.60.82.165'
MYSQL_USER = 'rating_token'
MYSQL_PW = '1qergg'
MYSQL_DB = 'rating_token'



# 实现scrapy_reids: 2.在settings文件中配置scrapy_redis
# REDIS数据链接
REDIS_URL = 'redis://127.0.0.1:6379/0'

# 去重容器类: 用于把已爬指纹存储到基于Redis的set集合中
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 调度器: 用于把待爬请求存储到基于Redis的队列
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 是不进行调度持久化:
# 如果是True, 当程序结束的时候, 会保留Redis中已爬指纹和待爬的请求
# 如果是False, 当程序结束的时候, 会清空Redis中已爬指纹和待爬的请求
SCHEDULER_PERSIST = True



# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'job_spider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  # 'Accept-Language': 'en',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'job_spider.middlewares.JobSpiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'job_spider.middlewares.JobSpiderDownloaderMiddleware': 543,
   # 'job_spider.middlewares.IPProxyDownloadMiddleware': 100,
   'job_spider.middlewares.UaIpDownloaderMiddleware': 100,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'job_spider.pipelines.JobSpiderPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


