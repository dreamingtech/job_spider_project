# -*- coding: utf-8 -*-
# pymongo这个包是阻塞的操作
import pymongo
import time
from twisted.internet import defer, reactor

from job_spider.items import BossSpiderItem


class JobSpiderMongoTwistedPipeline(object):
    """基于Twisted实现的mongodb异步客户端
    # https://zhuanlan.zhihu.com/p/44003499
    """
    def __init__(self, mongo_url):
        self.mongo_url = mongo_url

    # 从settings.py中读取MONGO_URL的配置
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
        )

    def open_spider(self, spider):
        if isinstance(spider, BossSpiderItem):
            self.client = pymongo.MongoClient(self.mongo_url)
            # 数据库: job_spider
            self.mongo_db = self.client.job_spider

    # 下面的操作是重点
    @defer.inlineCallbacks
    def process_item(self, item, spider):
        if not isinstance(item, BossSpiderItem):
            return item
        out = defer.Deferred()
        reactor.callInThread(self._insert, item, out)
        yield out
        defer.returnValue(item)

    def _insert(self, item, out):
        # time.sleep(10)
        collection = self.mongo_db[item['collection']]   # 数据要存入的collection集合
        collection.insert(dict(item))
        reactor.callFromThread(out.callback, item)

    def spider_closed(self, spider, reason):
        self.client.close()


import MySQLdb.cursors
from twisted.enterprise import adbapi


# 异步操作写入mysql数据库
class BossSpiderMysqlTwistedPipline(object):
    # from_settings和__init__这两个方法就能实现在启动spider时, 就把dbpool传递进来
    def __init__(self, dbpool):
        self.dbpool = dbpool

    # 在初始化时scrapy会调用from_settings方法, 将setting文件中的配置读入, 成为一个settings对象, 这种写法是固定的, 其中的参数不能修改.
    @classmethod
    def from_settings(cls, settings):
        dbparas = dict(
            host=settings["MYSQL_HOST"],
            # 可以在settings中设置此pipeline, 在此处放置断点, 进行debug, 查看能否导入. 在attribute中可以看到settings中定义的所有的值. F6执行, 就能看到取到了settings中设置的host的值了.
            port=settings["MYSQL_PORT"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USERNAME"],
            passwd=settings["MYSQL_PASSWORD"],
            # charset="utf8",
            charset="utf8mb4",
        # pymysql模块中也有类似的模块pymysql.cursors.DictCursor
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        # 创建twisted的mysql连接池, 使用twisted的连接池, 就能把mysql的操作转换为异步操作.
        # twisted只是提供了一个异步的容器, 并没有提供连接mysql的方法, 所以还需要MySQLdb的连接方法.
        # adbapi可以将mysql的操作变成异步化的操作. 查看ConectionPool, def __init__(self, dbapiName, *connargs, **connkw).
        # 需要指定使用的连接模块的模块名, 第一个参数是dbapiName, 即mysql的模块名MySQLdb. 第二个参数是连接mysql的参数, 写为可变化的参数形式. 查看MySQLdb的源码, 在from MySQLdb.connections import Connection中查看Connection的源码, 在class Connection中就能看到MySQLdb模块在连接mysql数据库时需要传递的参数. param这个dict中参数的名称要与其中的参数名称保持一致. 即与connections.py中 class Connection中的def __init__中定义的参数保持一致.
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparas)

        # 因为使用@classmethod把这个方法转换为类方法了, 所以cls就是指的MysqlTwistedPipline这个类, 所以cls(dbpool) 就相当于使用dbpool这个参数实例化MysqlTwistedPipline类的一个对象, 再把这个对象返回. 然后在init方法中接收这里创建的异步连接对象.
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql数据库的插入变成异步插入, 第一个参数是自定义的函数, runInteraction可以把这个函数的操作变成异步的操作. 第二个参数是要插入的数据, 这里是item.
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常, 这里也可以不传递item和spider
        query.addErrback(self.handle_error, item, spider)

    # 自定义错误处理, 处理异步插入的异常, 这里也可以不传递item和spider, 只传递failure即可.
    def handle_error(self, failure, item, spider):
        print(failure)
        print(item)

    # 执行具体的插入, 此时的cursor就是self.dbpool.runInteraction中传递过来的cursor, 使用这个cursor, 就可以把mysql的操作变成异步的操作. 并且此时也不用再手动执行commit的操作了.
    def do_insert(self, cursor, item):
        insert_sql = '''
            INSERT IGNORE INTO 
            article(title, create_date, article_url, url_object_id, front_image_url, front_image_path, comment_num, praise_num, fav_num, tags, content)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        # 注意, 当点赞数量为0时, 在jobbole.py中是无法取到值的, 也就无法进入到items.py中的input_processor进行处理, item中就没有这个字段的值, 所以这里对praise_num要使用get方法进行选择.
        cursor.execute(insert_sql, (item.get("title"), item.get("create_date"), item.get("article_url"), item.get("url_object_id"), item.get("front_image_url")[0], item.get("front_image_path",""), item.get("comment_num"), item.get("praise_num", "0"), item.get("fav_num"), item.get("tags"), item.get("content")))


from motor.motor_asyncio import AsyncIOMotorClient
from job_spider.settings import MONGO_URL


class BossSpiderMongoMotorPipeline(object):

    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        # 数据库: job_spider
        self.mongo_db = self.client.job_spider

    async def insert_position(self, collection, item):
        try:
            await collection.insert_one(dict(item))
        except:
            print("exist")

    def process_item(self, item, spider):

        if not isinstance(item, BossSpiderItem):
            return item
        collection = self.mongo_db[item['collection']]  # 数据要存入的collection集合
        self.insert_position(collection, item)

        return item
