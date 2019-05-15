# -*- coding: utf-8 -*-
import scrapy


class JobSpiderItem(scrapy.Item):
    '''通用item, 用于写入到关系型数据库'''
    spider_name = scrapy.Field()  # 来源spider, 通过此字段来区分是来自哪个爬虫的item
    publish_time = scrapy.Field()  # 发布时间, boss没有发布时间, 使用抓取时间来代替
    crawl_time = scrapy.Field()  # 爬虫爬取的时间

    category_info = scrapy.Field()  # 组合的分类信息, 根据此字段来对 crawl spider 类爬虫爬取的职位进行分类

    position_name = scrapy.Field()  # 职位名称
    position_url = scrapy.Field()  # 职位详情url地址
    position_benefits = scrapy.Field()  # 职位福利待遇
    position_tags = scrapy.Field()  # 本职位的标签, 所需技术/行业, 51job position_label和position_keyword合并, boss无此字段.
    # recruiting_num = scrapy.Field()  # 招聘人数, 只有zhaopin才有这个字段
    # position_type = scrapy.Field()  # 全职还是兼职, 只有lagou有这个字段

    position_status = scrapy.Field()  # 职位当前的状态, 是否处于招聘状态, 默认为True, boss无此字段, 再次爬取时为404, 就把它重置为False

    salary_range = scrapy.Field()  # 薪资范围
    working_city = scrapy.Field()  # 工作城市
    experience_required = scrapy.Field()  # 工作经验
    education_required = scrapy.Field()  # 学历

    # recruiter_name = scrapy.Field()  # 招聘人, boss独有字段
    # recruiter_title = scrapy.Field()   # 招聘人职位/title, boss独有字段

    position_desc = scrapy.Field()  # 职位描述详情
    # team_desc = scrapy.Field()  # 团队描述, boss独有字段
    # team_tags = scrapy.Field()  # 团队标签, boss独有字段
    working_address = scrapy.Field()  # 工作地址

    company_type = scrapy.Field()  # 民营还是国营, 51job字段, 外资企业
    company_intro = scrapy.Field()  # 公司简介, zhaopin 字段

    company_name = scrapy.Field()  # 公司名称
    company_url = scrapy.Field()  # 公司官网

    company_size = scrapy.Field()  # 公司规模
    company_industry = scrapy.Field()  # 公司所在的行业
    # company_financing_stage = scrapy.Field()  # 公司融资阶段, boss独有字段
    # company_representative = scrapy.Field()  # 法人代表, boss独有字段
    # company_registered_capital = scrapy.Field()  # 注册资金, boss独有字段
    # company_manage_status = scrapy.Field()  # 经营状态, boss独有字段
    # company_established_time = scrapy.Field()  # 成立时间, boss独有字段
    company_job_url = scrapy.Field()  # 在招聘网站上的公司主页
    company_name_abbr = scrapy.Field()  # 招聘网站上公司名称, boss独有字段

class CompanySpiderItem(scrapy.Item):
    """公司通用item, 用于写入到关系型数据库"""
    pass


class BossSpiderItem(scrapy.Item):
    spider_name = scrapy.Field()  # 来源spider, 通过此字段来区分是来自哪个爬虫的item
    publish_time = scrapy.Field()  # 发布时间, boss没有发布时间, 使用抓取时间来代替. # 以第一次爬取的时间为准, 以后不更新
    crawl_time = scrapy.Field()  # 爬虫爬取的时间

    category_info = scrapy.Field()  # 组合的分类信息, 根据此字段来对 crawl spider 类爬虫爬取的职位进行分类

    position_name = scrapy.Field()  # 职位名称
    position_url = scrapy.Field()  # 职位详情url地址
    position_benefits = scrapy.Field()  # 职位福利待遇
    # position_tags = scrapy.Field()  # 本职位的标签, 所需技术/行业, 51job position_label和position_keyword合并, boss无此字段.
    # recruiting_num = scrapy.Field()  # 招聘人数, 只有zhaopin才有这个字段
    # position_type = scrapy.Field()  # 全职还是兼职, 只有lagou有这个字段

    position_status = scrapy.Field()  # 职位当前的状态, 是否处于招聘状态, 默认为True, boss无此字段, 再次爬取时为404, 就把它重置为False
    position_fail_time = scrapy.Field()  # 职位失效时间, 使用第一次404的时间.

    salary_range = scrapy.Field()  # 薪资范围
    working_city = scrapy.Field()  # 工作城市
    experience_required = scrapy.Field()  # 工作经验
    education_required = scrapy.Field()  # 学历

    recruiter_name = scrapy.Field()  # 招聘人, boss独有字段
    recruiter_title = scrapy.Field()  # 招聘人职位/title, boss独有字段

    position_desc = scrapy.Field()  # 职位描述详情
    team_desc = scrapy.Field()  # 团队描述, boss独有字段
    team_tags = scrapy.Field()  # 团队标签, boss独有字段
    working_address = scrapy.Field()  # 工作地址

    company_name = scrapy.Field()  # 公司名称
    company_url = scrapy.Field()  # 公司官网
    company_job_url = scrapy.Field()  # 在招聘网站上的公司主页
    company_name_abbr = scrapy.Field()  # 招聘网站上公司名称缩写, boss独有字段


class BossCompanyItem(scrapy.Item):
    """boss直聘公司item"""
    spider_name = scrapy.Field()
    crawl_time = scrapy.Field()  # 爬虫爬取的时间
    company_job_url = scrapy.Field()  # 公司在招聘网站的主页
    company_name_abbr = scrapy.Field()  # 招聘网站上公司名称缩写, boss独有字段
    
    company_financing_stage = scrapy.Field()  # 公司融资阶段, boss独有字段
    company_size = scrapy.Field()  # 公司规模
    company_industry = scrapy.Field()  # 公司所在的行业
    company_benefits = scrapy.Field()  # 职位福利待遇
    company_position_num = scrapy.Field()  # 招聘职位数量, 以字典表示, 每次抓取时更新, 为以后数据分析准备
    company_intro = scrapy.Field()  # 公司简介, zhaopin 字段
    company_product_intro = scrapy.Field()  # 公司产品简介

    company_name = scrapy.Field()  # 工商信息中的公司名称
    company_url = scrapy.Field()  # 公司官网

    company_representative = scrapy.Field()  # 法人代表, boss独有字段
    company_registered_capital = scrapy.Field()  # 注册资金, boss独有字段
    company_manage_status = scrapy.Field()  # 经营状态, boss独有字段
    company_established_time = scrapy.Field()  # 成立时间, boss独有字段
    company_type = scrapy.Field()  # 民营还是国营, 51job字段, 外资企业
    company_registered_address = scrapy.Field()  # 公司注册地址
    company_unified_credit_code = scrapy.Field()  # 统一信用代码, boss字段
    company_business_scope = scrapy.Field()  # 公司经营范围
    company_executive_intro = scrapy.Field()  # 公司高管简介
    company_address = scrapy.Field()  # 公司地址


class LagouSpiderItem(scrapy.Item):
    spider_name = scrapy.Field()  # 来源spider, 通过此字段来区分是来自哪个爬虫的item
    publish_time = scrapy.Field()  # 发布时间, boss没有发布时间, 使用抓取时间来代替
    crawl_time = scrapy.Field()  # 爬虫爬取的时间

    category_info = scrapy.Field()  # 组合的分类信息, 根据此字段来对 crawl spider 类爬虫爬取的职位进行分类

    position_name = scrapy.Field()  # 职位名称
    position_url = scrapy.Field()  # 职位详情url地址
    position_benefits = scrapy.Field()  # 职位福利待遇
    position_tags = scrapy.Field()  # 本职位的标签, 所需技术/行业, 51job position_label和position_keyword合并, boss无此字段.
    recruiting_num = scrapy.Field()  # 招聘人数, 只有zhaopin才有这个字段
    position_type = scrapy.Field()  # 全职还是兼职, 只有lagou有这个字段

    position_status = scrapy.Field()  # 职位当前的状态, 是否处于招聘状态, 默认为True, boss无此字段, 再次爬取时为404, 就把它重置为False

    salary_range = scrapy.Field()  # 薪资范围
    working_city = scrapy.Field()  # 工作城市
    experience_required = scrapy.Field()  # 工作经验
    education_required = scrapy.Field()  # 学历

    # recruiter_name = scrapy.Field()  # 招聘人, boss独有字段
    # recruiter_title = scrapy.Field()   # 招聘人职位/title, boss独有字段

    position_desc = scrapy.Field()  # 职位描述详情
    # team_desc = scrapy.Field()  # 团队描述, boss独有字段
    # team_tags = scrapy.Field()  # 团队标签, boss独有字段
    working_address = scrapy.Field()  # 工作地址

    company_type = scrapy.Field()  # 民营还是国营, 51job字段, 外资企业
    # company_intro = scrapy.Field()  # 公司简介, zhaopin 字段

    company_name = scrapy.Field()  # 公司名称
    company_url = scrapy.Field()  # 公司官网

    company_size = scrapy.Field()  # 公司规模
    company_industry = scrapy.Field()  # 公司所在的行业

    company_financing_stage = scrapy.Field()  # 公司融资阶段, boss独有字段
    # company_representative = scrapy.Field()  # 法人代表, boss独有字段
    # company_registered_capital = scrapy.Field()  # 注册资金, boss独有字段
    # company_manage_status = scrapy.Field()  # 经营状态, boss独有字段
    # company_established_time = scrapy.Field()  # 成立时间, boss独有字段
    company_job_url = scrapy.Field()  # 在招聘网站上的公司主页
    company_name_abbr = scrapy.Field()  # 招聘网站上公司名称, boss独有字段


class LagouCompanyItem(scrapy.Item):
    spider_name = scrapy.Field()
    crawl_time = scrapy.Field()  # 爬虫爬取的时间
    company_job_url = scrapy.Field()  # 公司在招聘网站的主页
    company_name_abbr = scrapy.Field()  # 招聘网站上公司名称缩写, boss独有字段

    company_financing_stage = scrapy.Field()  # 公司融资阶段, boss独有字段
    company_size = scrapy.Field()  # 公司规模
    company_industry = scrapy.Field()  # 公司所在的行业
    company_benefits = scrapy.Field()  # 职位福利待遇
    company_position_num = scrapy.Field()  # 招聘职位数量, 以字典表示, 每次抓取时更新, 为以后数据分析准备
    company_intro = scrapy.Field()  # 公司简介, zhaopin 字段
    company_product_intro = scrapy.Field()  # 公司产品简介

    company_name = scrapy.Field()  # 工商信息中的公司名称
    company_url = scrapy.Field()  # 公司官网

    company_representative = scrapy.Field()  # 法人代表, boss独有字段
    company_registered_capital = scrapy.Field()  # 注册资金, boss独有字段
    company_manage_status = scrapy.Field()  # 经营状态, boss独有字段
    company_established_time = scrapy.Field()  # 成立时间, boss独有字段
    company_type = scrapy.Field()  # 民营还是国营, 51job字段, 外资企业
    company_registered_address = scrapy.Field()  # 公司注册地址
    company_unified_credit_code = scrapy.Field()  # 统一信用代码, boss字段
    company_business_scope = scrapy.Field()  # 公司经营范围
    company_executive_intro = scrapy.Field()  # 公司高管简介
    company_address = scrapy.Field()  # 公司地址

class Job51SpiderItem(scrapy.Item):
    spider_name = scrapy.Field()  # 来源spider, 通过此字段来区分是来自哪个爬虫的item
    publish_time = scrapy.Field()  # 发布时间, boss没有发布时间, 使用抓取时间来代替
    crawl_time = scrapy.Field()  # 爬虫爬取的时间

    category_info = scrapy.Field()  # 组合的分类信息, 根据此字段来对 crawl spider 类爬虫爬取的职位进行分类

    position_name = scrapy.Field()  # 职位名称
    position_url = scrapy.Field()  # 职位详情url地址
    position_benefits = scrapy.Field()  # 职位福利待遇
    position_tags = scrapy.Field()  # 本职位的标签, 所需技术/行业, 51job position_label和position_keyword合并, boss无此字段.
    recruiting_num = scrapy.Field()  # 招聘人数, 只有zhaopin才有这个字段
    position_type = scrapy.Field()  # 全职还是兼职, 只有lagou有这个字段

    position_status = scrapy.Field()  # 职位当前的状态, 是否处于招聘状态, 默认为True, boss无此字段, 再次爬取时为404, 就把它重置为False

    salary_range = scrapy.Field()  # 薪资范围
    working_city = scrapy.Field()  # 工作城市
    experience_required = scrapy.Field()  # 工作经验
    education_required = scrapy.Field()  # 学历

    # recruiter_name = scrapy.Field()  # 招聘人, boss独有字段
    # recruiter_title = scrapy.Field()   # 招聘人职位/title, boss独有字段

    position_desc = scrapy.Field()  # 职位描述详情
    # team_desc = scrapy.Field()  # 团队描述, boss独有字段
    # team_tags = scrapy.Field()  # 团队标签, boss独有字段
    working_address = scrapy.Field()  # 工作地址

    company_type = scrapy.Field()  # 民营还是国营, 51job字段, 外资企业
    company_intro = scrapy.Field()  # 公司简介, 51job, zhaopin 字段

    company_name = scrapy.Field()  # 公司名称
    company_url = scrapy.Field()  # 公司官网

    company_size = scrapy.Field()  # 公司规模
    company_industry = scrapy.Field()  # 公司所在的行业

    # company_financing_stage = scrapy.Field()  # 公司融资阶段, boss独有字段
    # company_representative = scrapy.Field()  # 法人代表, boss独有字段
    # company_registered_capital = scrapy.Field()  # 注册资金, boss独有字段
    # company_manage_status = scrapy.Field()  # 经营状态, boss独有字段
    # company_established_time = scrapy.Field()  # 成立时间, boss独有字段
    company_job_url = scrapy.Field()  # 在招聘网站上的公司主页
    company_name_abbr = scrapy.Field()  # 招聘网站上公司名称, boss独有字段


class ZhaopinSpiderItem(scrapy.Item):
    spider_name = scrapy.Field()  # 来源spider, 通过此字段来区分是来自哪个爬虫的item
    publish_time = scrapy.Field()  # 发布时间, boss没有发布时间, 使用抓取时间来代替
    crawl_time = scrapy.Field()  # 爬虫爬取的时间

    category_info = scrapy.Field()  # 组合的分类信息, 根据此字段来对 crawl spider 类爬虫爬取的职位进行分类

    position_name = scrapy.Field()  # 职位名称
    position_url = scrapy.Field()  # 职位详情url地址
    position_benefits = scrapy.Field()  # 职位福利待遇
    position_tags = scrapy.Field()  # 本职位的标签, 所需技术/行业, 51job position_label和position_keyword合并, boss无此字段. 
    recruiting_num = scrapy.Field()  # 招聘人数, 只有zhaopin才有这个字段
    # position_type = scrapy.Field()  # 全职还是兼职, 只有lagou有这个字段

    position_status = scrapy.Field()  # 职位当前的状态, 是否处于招聘状态, 默认为True, boss无此字段, 再次爬取时为404, 就把它重置为False

    salary_range = scrapy.Field()  # 薪资范围
    working_city = scrapy.Field()  # 工作城市
    experience_required = scrapy.Field()  # 工作经验
    education_required = scrapy.Field()  # 学历

    # recruiter_name = scrapy.Field()  # 招聘人, boss独有字段
    # recruiter_title = scrapy.Field()   # 招聘人职位/title, boss独有字段

    position_desc = scrapy.Field()  # 职位描述详情
    # team_desc = scrapy.Field()  # 团队描述, boss独有字段
    # team_tags = scrapy.Field()  # 团队标签, boss独有字段
    working_address = scrapy.Field()  # 工作地址

    company_type = scrapy.Field()  # 民营还是国营, 51job字段, 外资企业
    company_intro = scrapy.Field()  # 公司简介, 51job, zhaopin 字段

    company_name = scrapy.Field()  # 公司名称
    company_url = scrapy.Field()  # 公司官网

    company_size = scrapy.Field()  # 公司规模
    company_industry = scrapy.Field()  # 公司所在的行业

    # company_financing_stage = scrapy.Field()  # 公司融资阶段, boss独有字段
    # company_representative = scrapy.Field()  # 法人代表, boss独有字段
    # company_registered_capital = scrapy.Field()  # 注册资金, boss独有字段
    # company_manage_status = scrapy.Field()  # 经营状态, boss独有字段
    # company_established_time = scrapy.Field()  # 成立时间, boss独有字段
    company_job_url = scrapy.Field()  # 在招聘网站上的公司主页
    company_name_abbr = scrapy.Field()  # 招聘网站上公司名称, boss独有字段
