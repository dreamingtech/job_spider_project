# -*- coding: utf-8 -*-

import time
import redis  # redis 2.10.6
import random
import json
import requests
from twisted.internet.defer import DeferredLock

from job_spider.settings import PROXY_API_LIST
from job_spider.settings import PROXY_REDIS_HOST, PROXY_REDIS_PORT, PROXY_REDIS_DB
from job_spider.settings import CRAWL_NODE_NUM, SPIDER_NAMES
from job_spider.utils.log import logger


class ProxyPool(object):
    """从付费api中获取代理地址并构建代理池"""

    def __init__(self, spider_name):
        """
        初始化付费代理池, 短效代理
        ip, port, 来源网站, 获取时间, 是否被封, 是否过期, 过期时间
        """
        self.redis = redis.StrictRedis(host=PROXY_REDIS_HOST, port=PROXY_REDIS_PORT, db=PROXY_REDIS_DB)
        self.lock = DeferredLock()
        self._init_proxy_pool(spider_name)

    def _init_proxy_pool(self, spider_name):
        """创建代理池时自动从api获取特定数量的代理地址"""
        proxy_num = self.get_proxy_num(spider_name)
        print("初始代理数量:", proxy_num)
        # 判断当前爬虫代理池中的代理数量是否小于爬虫的节点数
        while proxy_num < CRAWL_NODE_NUM:
            self._add_proxy()
            proxy_num = self.get_proxy_num(spider_name)
            print("代理数量:", proxy_num)

    def _get_proxy_from_api(self):
        '''从付费代理 api 中获取代理'''
        random.shuffle(PROXY_API_LIST)
        # '{"code":"3001","msg":"提取频繁请按照规定频率提取!"}'
        # '{"code":"0","msg":[{"port":"35379","ip":"117.60.2.113"}]}'
        # {"ERRORCODE":"10055","RESULT":"提取太频繁,请按规定频率提取!"}'
        # {"ERRORCODE":"0","RESULT":[{"port":"48448","ip":"115.203.196.254"}]}'
        proxy = {}
        while True:
            for api in PROXY_API_LIST:
                print(api)
                ip_port_list = []
                response = requests.get(api)
                proxy["gen_time"] = int(time.time()*1000)
                js_str = json.loads(response.text)
                if "mogumiao" in api:
                    # 来自蘑菇代理
                    proxy["orgin"] = "mogu"
                    if js_str.get('code') == '0':
                        ip_port_list = js_str.get("msg")
                elif "xdaili" in api:
                    # 来自讯代理
                    proxy["orgin"] = "xdaili"
                    if js_str.get('ERRORCODE') == '0':
                        ip_port_list = js_str.get("RESULT")
                if ip_port_list:
                    proxy_list = []
                    for ip_port in ip_port_list:
                        proxy["ip"] = ip_port.get("ip")
                        proxy["port"] = ip_port.get("port")
                        proxy_list.append(proxy)
                    return proxy_list

                else:
                    print("提取太频繁, 等待中...")
                    logger.warning("api {} 提取太频繁, 等待中".format(api))
                    time.sleep(random.randint(1, 5))

    def _get_redis_proxy_key(self, spider_name):
        return "REDIS_PROXY_KEY_{}".format(spider_name.upper())

    def _get_blacked_redis_proxy_key(self, spider_name):
        return "REDIS_PROXY_KEY_{}_BLACKED".format(spider_name.upper())

    def _add_proxy(self):
        '''
        向所有爬虫的代理池中添加一个代理
        :param spider_name: redis_key 以 spider_name 开头的
        :return: None
        '''
        self.lock.acquire()
        proxy = {}
        # 因为代理池是生成器, 所以要使用 for 循环获取代理
        proxy_list = self._get_proxy_from_api()
        print("proxy_list", proxy_list)
        for proxy in proxy_list:
            logger.warning("从api获取的代理是: {}:{}".format(proxy.get("ip"), proxy.get("port")))
            for spider_name in SPIDER_NAMES:
                redis_proxy_key = self._get_redis_proxy_key(spider_name)
                if redis.__version__ in ['3.2.1']:
                    mapping = {
                        json.dumps(proxy): proxy.get("gen_time")
                    }
                    self.redis.zadd(redis_proxy_key, mapping)
                else:  # redis 2.10.6
                    self.redis.zadd(redis_proxy_key, proxy.get("gen_time"), json.dumps(proxy))
                logger.info("spider: {} 代理池添加代理 {}:{} 成功".format(spider_name, proxy.get("ip"), proxy.get("port")))
        self.lock.release()

    def get_proxy(self, spider_name):
        """从代理池中获取一个对本网站有效的ip"""
        # self.lock.acquire()
        redis_proxy_key = self._get_redis_proxy_key(spider_name)
        while True:
            time.sleep(0.1)
            proxy_list = self.redis.zrange(redis_proxy_key, 0, 0)
            print("proxy_list", proxy_list)
            # 如果代理池中的代理数大于 0 , 就获取代理, 同时把它从 代理池中删除
            if proxy_list:
                proxy = json.loads(proxy_list[0])
                self.redis.zrem(redis_proxy_key, json.dumps(proxy))
                logger.info("spider: {} 从代理池获取代理 {}:{} 成功".format(spider_name, proxy.get("ip"), proxy.get("port")))
                # self.lock.release()
                return proxy
                # return "https://{}:{}".format(proxy.get("ip"), proxy.get("port"))
            # 如果代理池中的代理数等于0, 就添加代理, 然后再进行循环, 直到获取到一个代理
            else:
                # self.lock.release()
                logger.info("代理池 {} 中代理数量不足, 从api获取代理".format(redis_proxy_key))
                self._add_proxy()

    def _remove_proxy(self, proxy, spider_name):
        '''从代理池中移除特定的代理'''
        # self.lock.acquire()
        redis_proxy_key = self._get_redis_proxy_key(spider_name)
        self.redis.zrem(redis_proxy_key, json.dumps(proxy))
        logger.info("spider: {} 代理池删除代理 {}:{} 成功".format(spider_name, proxy.get("ip"), proxy.get("port")))
        # self.lock.release()

    def mark_as_blacked(self, proxy, spider_name, blacked_time):
        """标记某个代理地址被某个网站列入黑名单, """
        # self.lock.acquire()
        blacked_redis_proxy_key = self._get_blacked_redis_proxy_key(spider_name)
        # 因为在获取代理时已经从可用代理池中删除了代理, 所以这里不用再删除代理即可
        # self._remove_proxy(proxy, spider_name)
        proxy["blacked_time"] = blacked_time
        logger.info("spider: {} 代理 {}:{} 于 {} 时间被封".format(spider_name, proxy.get("ip"), proxy.get("port"), blacked_time))

        if redis.__version__ in ['3.2.1']:
            mapping = {
                json.dumps(proxy): proxy.get("gen_time")
            }
            self.redis.zadd(blacked_redis_proxy_key, mapping)
        else:
            self.redis.zadd(blacked_redis_proxy_key, proxy.get("gen_time"), json.dumps(proxy))
        # self.lock.release()

    def get_proxy_num(self, spider_name):
        """从代理池中获取当前可用的代理数量"""
        redis_proxy_key = self._get_redis_proxy_key(spider_name)
        proxy_num = self.redis.zcard(redis_proxy_key)
        return proxy_num

    def is_blacked(self, proxy, spider_name):
        """判断某个代理是否被某个网站封锁"""
        blacked_redis_proxy_key = self._get_blacked_redis_proxy_key(spider_name)
        # 未被封 result = None > True
        return True if self.redis.zscore(blacked_redis_proxy_key, json.dumps(proxy)) else False


if __name__ == '__main__':

    proxy_pool = ProxyPool()
    proxy = proxy_pool.get_proxy(spider_name="lagou")
    print(proxy)
