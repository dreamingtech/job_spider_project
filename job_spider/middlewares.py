# -*- coding: utf-8 -*-
import scrapy
import time
import requests

from twisted.internet import defer
from twisted.internet.defer import DeferredLock
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError, ConnectionLost, TCPTimedOutError, ConnectionDone
from job_spider.utils.yundama import indetify_by_response
from job_spider.utils.ua import get_ua
from job_spider.utils.proxy import ProxyPool
from job_spider.utils.log import logger
from selenium import webdriver
from selenium.webdriver import ActionChains

class UaIpDownloaderMiddleware(object):

    def __init__(self, ua=''):
        # 初始时从api获取代理地址, 并给所有代理都设置为这个代理
        # super(RandomUAIPDownloaderMiddleware, self).__init__()
        self.user_agent = get_ua()
        self.exception_list = (
            defer.TimeoutError, TimeoutError, ConnectionRefusedError, ConnectError, ConnectionLost, TCPTimedOutError, ConnectionDone
        )
        self.lock = DeferredLock()
        self.spider_name = "boss"
        self.proxy_pool = ProxyPool(self.spider_name)
        print("获取代理")
        self.proxy = self.proxy_pool.get_proxy(self.spider_name)
        self.ip_port = "https://{}:{}".format(self.proxy.get("ip"), self.proxy.get("port"))

    def _update_proxy(self, request):

        self.lock.acquire()
        print("上锁")
        logger.warning("更新代理 <{}>".format(request.meta.get('proxy')))
        # 如果失效的代理不在代理黑名单中, 表示这是这个代理地址第一次失效, 就执行更新代理的操作.

        if not self.proxy_pool.is_blacked(self.proxy, self.spider_name):
            # 如果代理过期, 就把它添加到代理黑名单列表中
            self.proxy_pool.mark_as_blacked(self.proxy, self.spider_name, int(time.time() * 1000))
            logger.warning("添加 <{}> 到黑名单".format(request.meta.get('proxy')))
            # 生成新的 ua 和 ip
            self.user_agent = get_ua()
            self.proxy = self.proxy_pool.get_proxy(self.spider_name)
            self.ip_port = "https://{}:{}".format(self.proxy.get("ip"), self.proxy.get("port"))
        # 把ip添加到黑名单后, 设置其代理为None, 再次经过 process_request 处理后添加新的代理
        request.meta["proxy"] = None
        request.headers.setdefault('User-Agent', None)

        self.lock.release()
        print("解锁")

    def process_request(self, request, spider):

        # 把更新代理的操作都放在process_request中进行. 这样, 不论是第一次的请求, 还是
        # 判断request中使用的代理, 如果它不等于当前的代理, 就把它设置为当前的代理
        print("请求的代理地址:", request.meta.get('proxy'))
        print("self.ip_port: ", self.ip_port)
        if request.meta.get('proxy') != self.ip_port:
            request.headers.setdefault('User-Agent', self.user_agent)
            request.meta["proxy"] = self.ip_port
            print("请求的代理地址:", request.meta.get('proxy'))
            print("self.ip_port: ", self.ip_port)

    def process_response(self, request, response, spider):
        # 如果出现了验证码, 就使用云打码平台进行识别
        # response.url = https://www.zhipin.com/captcha/popUpCaptcha?redirect=https://www.zhipin.com/gongsi/ba1fd0561b80a2121nBy0tS5EQ~~.html
        if "captcha" in response.url:
            # 提取出form表单的action地址
            # /captcha/verifyCaptcha?redirect=https://www.zhipin.com/gongsi/ba1fd0561b80a2121nBy0tS5EQ~~.html
            action_url = response.xpath('//form[@action]/@action').extract_first()
            action_url = response.urljoin(action_url)

            # 提取出随机生成的验证码字符串.
            # cNLEI5hl48W3szGtFewZt1GzOxe7Wo8y
            random_key = response.xpath('//input[@name="randomKey"]/@value').extract_first()

            headers = {
                "User-Agent": request.headers.get("User-Agent"),
                "Referer": response.url
            }
            # 构造出请求的url地址
            # https://www.zhipin.com/captcha?randomKey=Djn9wfQjAO2EuQrm4WL1uNY8V2xrKTN2
            captcha_url = "https://www.zhipin.com/captcha?randomKey={}".format(random_key)
            # 发送请求获取验证码
            captcha_response = requests.get(captcha_url, headers=headers)
            # 使用云打码平台识别验证码
            captcha = indetify_by_response(captcha_response.content)
            # 构造发送验证码的请求数据.
            post_data = {
                "randomKey": random_key,
                "captcha": captcha
            }

            # 使用FormRequest构造post请求.
            return scrapy.FormRequest(url=action_url, formdata=post_data, headers=headers)

        elif "slider" in response.url:
            logger.warning("出现滑动验证码: {}, 状态码: {}".format(request.url, response.status))
            # 如果出现了滑动验证码, 对滑动验证码进行处理
            print("处理滑动验证码")
            self._update_proxy(request)
            return request.replace(dont_filter=True)

        # 如果返回的response状态不是200，或者出现了验证码, 就重新获取代理.
        # """有点过于武断, 需要进行进一步的判断"""
        elif response.status != 200:
            logger.warning("Proxy {}, 链接 {} 出错, 状态码为 {}".format(request.meta['proxy'], request.url, response.status))
            self._update_proxy(request)
            return request.replace(dont_filter=True)

        return response


    def process_exception(self, request, exception, spider):

        # 如果出现了上面列表中的异常, 就认为代理失效了. 由于scrapy使用的是异步框架, 所以代理失效时会有很多个请求同时出现上面列表中的异常, 同时进入到这里的代码中执行.
        # 如果按照一般的思路, 把更新代理的操作放在这里, 那么所有异常的请求进入此代码后都要更新代理, 都要向api发送请求获取代理地址, 此时就会出现代理请求太频繁的提示.
        # 这里使用的方法是, 只要出现了认为是代理失效的异常, 就把请求的proxy和user-agent设置为None, 同时设置另一个条件判断产生异常的代理是否等于self.proxy, 当异常发生时, 必定会有先后的顺序, 第1个异常的请求进入这里时, 满足此条件, 执行下面的代码, 更新self.user_agent和self.proxy.
        # 当以后发生异常的请求再次进入到这里的逻辑时, 因为第1个请求已经更新了self.proxy的值, 就不能满足第2个if判断中的条件, 就不会执行更新代理的操作了, 这样就避免了所有发生异常的请求同时请求api更新代理的情况.
        print("\n")
        print("处理异常")
        print("\n")
        if isinstance(exception, self.exception_list):
            logger.warning("Proxy {} 链接出错 {}".format(request.meta['proxy'], exception))
            self._update_proxy(request)

        return request.replace(dont_filter=True)
