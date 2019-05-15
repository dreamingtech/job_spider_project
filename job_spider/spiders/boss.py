# -*- coding: utf-8 -*-
import time
import scrapy
from job_spider.items import BossSpiderItem
import re


class BossSpider(scrapy.Spider):
    name = 'boss'
    allowed_domains = ['zhipin.com']
    start_urls = ['https://www.zhipin.com/']

    def parse(self, response):
        """# 从主页中解析出职位列表页的url"""
        # 主分类
        main_cates = response.xpath('(//div[@class="job-menu"]|//div[@class="all-box"])/dl')
        for main_cate in main_cates:
            main_cate_name = main_cate.xpath('./dd/b/text()').extract_first()
            # 次分类
            sub_cates = main_cate.xpath('./div[@class="menu-sub"]//li')
            for sub_cate in sub_cates:
                sub_cate_name = sub_cate.xpath('./h4/text()').extract_first()
                # 职位分类
                cates = sub_cate.xpath('./div/a')
                for cate in cates:
                    cate_name = cate.xpath('./text()').extract_first()
                    # 提取到的是部分的url地址, 要拼接为完整的url
                    cate_url_local = response.urljoin(cate.xpath('./@href').extract_first())
                    # 提取到的url默认是ip所在城市的url, 要修改为全国的url
                    # 上海 href="/c101020100-p100199/", 全国 href="/c101020100-p100199/"
                    cate_url_national = re.sub(r'c\d+', 'c100010000', cate_url_local)
                    # 把分类信息组合成 "销售业务-销售代表" 的形式
                    category_info = "{}-{}-{}".format(main_cate_name, sub_cate_name, cate_name)
                    meta = {"category_info": category_info}
                    # meta = {"main_cate_name": main_cate_name, "sub_cate_name": sub_cate_name, "cate_name": cate_name}
                    # 在列表页解析时设置dont_fileter=True, 这样, 在再次运行爬虫时就能再次提取信息, 实现增量爬虫
                    # 把job_item使用meta传递过去,
                    yield scrapy.Request(url=cate_url_national, callback=self.parse_job_list, dont_filter=True, meta=meta)
                    # 测试代码
                    # break
                # break
            # break

    def parse_job_list(self, response):
        """解析职位列表页"""
        # 在职位列表页中只提取出职位详情页的url, 职位的详情信息都在职位详情页中提取
        position_urls = response.xpath('//div[@class="info-primary"]/h3/a/@href').extract()
        # 发布日期只能在列表页中获取到, 所以需要先在列表页中提取信息, 再在详情页中提取信息
        # 列表页中只提取出职位的url即可.
        for position_url in position_urls:
            yield scrapy.Request(url=response.urljoin(position_url), callback=self.parse_job_detail, meta=response.meta)
            # 测试代码
            # break
        # 提取下一页的url
        next_page_url = response.xpath('//div[@class="page"]/a[@class="next"]/@href').extract_first(default='')
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            # 解析下一页, 指定dont_filter=True, 就可以实现增量爬虫了.
            yield scrapy.Request(url=next_page_url, dont_filter=True, callback=self.parse_job_list, meta=response.meta)

    def parse_job_detail(self, response):
        """解析职位详情页信息"""
        # job_infos中只有一个元素.
        position_info = response.xpath('//div[@class="job-primary detail-box"]/div[@class="info-primary"]').extract_first()
        # 职位状态
        position_status = position_info.xpath('./div[@class="job-status"]/text()').extract_first()
        # 职位名称
        position_name = position_info.xpath('./div[@class="name"]/h1/text()').extract_first()
        # 工资范围
        salary_range = position_info.xpath('./div[@class="name"]/span[@class="salary"]/text()').extract_first().strip()
        # 工作要求: 城市, 经验, 学历
        job_requirements = position_info.xpath('./p/text()').extract()
        # 工作城市
        working_city = job_requirements[0] if len(job_requirements) > 0 else ""
        # 经验
        experience_required = job_requirements[1] if len(job_requirements) > 1 else ""
        # 学历
        education_required = job_requirements[2] if len(job_requirements) > 2 else ""
        # 职位标签
        position_advantage = ",".join(position_info.xpath('.//div[@class="job-tags"]/span/text()').extract())

        # 招聘人名称
        recruiter_name = response.xpath('//div[@class="detail-op"]/h2/text()').extract_first()
        # 招聘人职位
        recruiter_title = response.xpath('//div[@class="detail-op"]/p[@class="gray"]/em/preceding-sibling::text()').extract_first()

        # 职位描述
        positiion_desc_list = response.xpath('//h3[contains(text(), "职位描述")]/following-sibling::div[@class="text"]/text()').extract()

        position_desc = ''.join([i.strip()+'\n' for i in positiion_desc_list if i])

        # 团队介绍
        team_desc_list = response.xpath('//h3[contains(text(), "团队介绍")]/following-sibling::div[@class="text"]/text()').extract()
        team_desc = ''.join([i.strip() for i in team_desc_list if i])

        # 职位标签
        team_tags_list = response.xpath('//div[@class="job-sec"]/div[@class="job-tags"]/span/text()').extract()
        team_tags = ','.join([i.strip() for i in team_tags_list if i])

        # 工作地址
        working_address = response.xpath('//div[@class="location-address"]/text()').extract_first()

        # 工商信息-公司名称
        company_name = response.xpath('//h3[contains(text(), "工商信息")]/following-sibling::div[@class="name"]/text()').extract_first()

        # 公司详情页
        company_job_url = response.xpath('//a[@ka="job-detail-company"]/@href').extract_first()
        company_job_url = response.urljoin(company_job_url)
        # 公司简称
        company_name_abbr = response.xpath('//a[@ka="job-detail-company"]/@title').extract_first()
        # 公司官网
        company_url = response.xpath('//i[@class="icon-net"]/following-sibling::text()').extract_first()

        boss_item = BossSpiderItem(
            spider_name=self.name,  # 以爬虫名作为来源
            crawl_time = int(time.time()),
            publish_time = int(time.time()),   # 以第一次爬取的时间为准, 以后不更新
            category_info = response.meta.get("category_info"),
            position_status = position_status,
            position_name = position_name,
            position_url = response.request.url,  # 不使用response.url
            salary_range = salary_range,
            working_city = working_city,
            experience_required = experience_required,
            education_required = education_required,
            position_advantage = position_advantage,
            recruiter_name = recruiter_name,
            recruiter_title = recruiter_title,
            job_desc = position_desc,
            team_desc = team_desc,
            team_tags = team_tags,
            company_name_abbr= company_name_abbr,
            company_job_url = company_job_url,
            working_address = working_address,
            company_name = company_name,
        )

        yield boss_item

    def parse_company_info(self, response):
        """解析公司在招聘网站上的主页的信息"""

        # 工商信息-公司名称
        company_name = response.xpath('').extract_first()

        # 法人代表
        company_representative = response.xpath('').extract_first()
        # 注册资金
        company_registered_capital = response.xpath('').extract_first()
        # 成立时间
        company_established_time = response.xpath('').extract_first()
        # 企业类型
        company_type = response.xpath('').extract_first()
        # 经营状态
        company_manage_status = response.xpath('').extract_first()
        # 公司详情页
        company_job_url = response.xpath('').extract_first()
        company_job_url = response.urljoin(company_job_url)
        # 公司简称
        company_name_abbr = response.xpath('').extract_first()
        # 公司融资阶段
        company_financing_stage = response.xpath('').extract_first()
        # 公司规模
        company_size = response.xpath('').extract_first()
        # 公司领域
        company_industry = response.xpath('').extract_first()
        # 公司官网
        company_url = response.xpath('').extract_first()
        pass

    def parse_company_position(self, response):
        """解析公司在招聘网站上的所有职位信息"""
        pass
