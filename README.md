# 招聘网站爬虫

## 目标

boss直聘, lagou, 51job招聘网站爬虫

## 代理池

### 设置原理: 

基于 redis 有序集合完成的代理池

每个爬虫维护一个代理池和一个被封代理池

### 数据结构:

"{\"gen_time\": 1557118454373, \"orgin\": \"mogu\", \"ip\": \"117.26.229.1\", \"port\": \"42447\"}"

包括 生成时间, 来源网站, ip, port, 被封时间

### 包含方法

function:

​    _add_proxy: 向所有爬虫的代理池中添加一个代理

​    _get_blacked_redis_proxy_key:

​    _get_proxy_from_api: 从付费代理 api 中获取代理

​    _get_redis_proxy_key:

​    _init_proxy_pool: 创建代理池时自动从api获取特定数量的代理地址

​    _remove_proxy: 从代理池中移除特定的代理

​    get_proxy: 从代理池中获取一个对本网站有效的ip

​    get_proxy_num: 从代理池中获取当前可用的代理数量

​    is_blacked: 判断某个代理是否被某个网站封锁

​    mark_as_blacked: 标记某个代理地址被某个网站列入黑名单, 



### 细节说明

对每一个爬虫维护一个代理池

使用 redis 有序集合. 对每一个爬虫维护一个代理池, 每次获取代理时都添加到所有的代理池中

setttins.py 中设置爬虫的爬取节点数 CRAWL_NODE_NUM

初始化代理池时从api获取 CRAWL_NODE_NUM 个代理添加到所有爬虫的代理池中.

因为使用的是短期代理, 代理有效期为 1-5 min, 从代理池中获取一个代理ip时, 就把它从代理池中删除, 一直使用到代理过期或被封, 记录失效时间, 把它添加到该爬虫的被封代理池中. 然后重新从代理池中获取代理.

如果从代理池中获取代理时代理数不足, 就从 代理 api 中获取代理并添加到所有爬虫的代理池中.

过期的代理可以使用百度来检测, 也可以不关注过期时间, 因为过期的一定是失效的, 无法正常爬取到数据, 可以认为是被网站列入黑名单了, 只需要记录被封的代理. 把所有 spider 最晚的失效时间作为过期时间即可.


## 下载中间件设置

### process_request

该方法中对所有的request请求设置代理

### process_response

该方法对响应进行处理, 如果出现了 字母-数字  型验证码, 就调用 云打码平台进行验证码识别

如果出现了 滑动验证码, 暂时以更换代理的方法解决

如果状态码不等于 200, 暂时以更换代理的方法解决

### process_exception

对异常进行处理, 如果出现了 特定的异常, 就更换代理


## item 设置

### 分类信息
boss, lagou 为三分类
zhaopin, 51job 为二分类
把分类信息组合成 "销售业务-销售代表" 的形式


### 改进

1. 职位信息和公司信息分开爬取, 使用不同的item
2. 在爬虫中使用 crawl spider 类爬虫, 爬取更多职位信息和公司信息
1.1. 修改调度器, crawl spider 类爬虫的响应放到 scrapy spider 类爬虫的响应处理完后再进行
1.2. 每个招聘网站新增 crawl spider 类爬虫, 在每次 scrapy spider 类爬虫运行结束后运行此爬虫


### 其它

由智联招聘主页分类导航
https://www.zhaopin.com/
得到的职位列表页是ajax加载出来的

访问地址:
https://sou.zhaopin.com/?jl=538&kw=Python&kt=3
数据加载地址:
https://fe-api.zhaopin.com/c/i/sou?pageSize=90&cityId=538&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=Python&kt=3&_v=0.10527862&x-zp-page-request-id=73fe3c87cf604ec2a6daf8f4af4c8b09-1557884002245-960295

但是由
https://jobs.zhaopin.com/
得到的职位列表页则是直接由html加载而来的
