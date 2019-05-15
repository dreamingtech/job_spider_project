# -*- coding: utf-8 -*-

from job_spider.utils.proxy import ProxyPool as BaseClass
import time


class ProxyPool(BaseClass):

    def _get_proxy_from_api(self):
        '''从付费代理 api 中获取代理'''
        proxy_list = [{"gen_time": 1557105786531, "orgin": "mogu", "ip": "123.245.11.88", "port": "27457"}, {"gen_time": 1557105787678, "orgin": "xdaili", "ip": "183.166.125.23", "port": "37186"}, {"gen_time": 1557105787786, "orgin": "mogu", "ip": "121.205.151.166", "port": "37832"}, {"gen_time": 1557105787880, "orgin": "mogu", "ip": "121.230.252.182", "port": "24482"}, {"gen_time": 1557105790265, "orgin": "mogu", "ip": "117.69.200.211", "port": "24078"}, {"gen_time": 1557105790408, "orgin": "mogu", "ip": "180.122.149.167", "port": "49868"}, {"gen_time": 1557105791651, "orgin": "mogu", "ip": "114.229.205.59", "port": "33490"}, {"gen_time": 1557105791792, "orgin": "mogu", "ip": "123.163.133.221", "port": "42083"}, {"gen_time": 1557105794126, "orgin": "mogu", "ip": "1.199.132.249", "port": "20905"}, {"gen_time": 1557105794229, "orgin": "mogu", "ip": "114.232.195.195", "port": "27999"}, {"gen_time": 1557105794339, "orgin": "xdaili", "ip": "61.154.91.154", "port": "34066"}, {"gen_time": 1557105797533, "orgin": "mogu", "ip": "27.156.214.115", "port": "35246"}, {"gen_time": 1557105798702, "orgin": "mogu", "ip": "49.72.4.105", "port": "23563"}, {"gen_time": 1557105798803, "orgin": "mogu", "ip": "1.194.191.46", "port": "22554"}, {"gen_time": 1557105798952, "orgin": "xdaili", "ip": "180.108.206.170", "port": "31846"}, {"gen_time": 1557105800133, "orgin": "mogu", "ip": "117.95.74.85", "port": "45656"}, {"gen_time": 1557105806393, "orgin": "mogu", "ip": "140.237.115.183", "port": "25879"}, {"gen_time": 1557105806535, "orgin": "mogu", "ip": "60.169.36.146", "port": "20021"}, {"gen_time": 1557105806652, "orgin": "xdaili", "ip": "114.232.170.21", "port": "43246"}, {"gen_time": 1557105806803, "orgin": "mogu", "ip": "36.99.206.250", "port": "20111"}]

        for proxy in proxy_list:
            yield proxy


if __name__ == '__main__':

    proxy_pool = ProxyPool()
    proxy = proxy_pool.get_proxy(spider_name="lagou")
    print(proxy)
    proxy = proxy_pool.get_proxy(spider_name="lagou")
    print(proxy)
    proxy = proxy_pool.get_proxy(spider_name="lagou")
    print(proxy)
    # proxy = proxy_pool.get_proxy(spider_name="lagou")
    # print(proxy)
    # proxy = proxy_pool.get_proxy(spider_name="lagou")
    # print(proxy)
    # proxy = proxy_pool.get_proxy(spider_name="lagou")
    # print(proxy)
    proxy = {"gen_time": 1556783012845, "orgin": "mogu", "ip": "27.152.25.114", "port": "20553"}
    proxy_pool.mark_as_blacked(proxy, "lagou", int((time.time()*1000)))
