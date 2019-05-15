# -*- coding: utf-8 -*-
import scrapy
from job_spider.items import Job51SpiderItem

class Job51Spider(scrapy.Spider):
    name = 'job51'
    allowed_domains = ['51job.com']
    start_urls = ['https://jobs.51job.com/']

    def parse(self, response):
        # 主分类分组
        main_cates = response.xpath('//div[@class="e e5"]')
        for main_cate in main_cates:
            main_cate_name = main_cate.xpath('./p//strong/text()').extract_first()
            # 次分类分组
            sub_cates = main_cate.xpath('./div[@class="lkst"]/a')
            for sub_cate in sub_cates:
                sub_cate_name = sub_cate.xpath('./text()').extract_first()
                sub_cate_url = sub_cate.xpath('./@href').extract_first()
                # print(sub_cate_name)
                # print(sub_cate_url)
                # 把分类信息组合成 "销售业务-销售代表" 的形式
                cate_info = "{}-{}".format(main_cate_name, sub_cate_name)
                meta = {"cate_info": cate_info}
                # meta = {"main_cate_name": main_cate_name, "sub_cate_name": sub_cate_name}
                # 在列表页解析时设置dont_fileter=True, 这样, 在再次运行爬虫时就能再次提取信息, 实现增量爬虫
                # 把job_item使用meta传递过去,
                yield scrapy.Request(url=sub_cate_url, callback=self.parse_job_list, dont_filter=True, meta=meta)
            #     break
            # break

    # 从列表页中提取详情页url
    def parse_job_list(self, response):
        positions = response.xpath('//div[@class="detlist gbox"]/div[contains(@class, "e")]')
        for position in positions:
            position_url = position.xpath('.//span[@class="title"]/a/@href').extract_first()
            yield scrapy.Request(url=position_url, callback=self.parse_job_detail, meta=response.meta)
            # 测试代码
            # break

        # 提取出下一页的url
        next_page_url = response.xpath('//div[@id="cppageno"]//a[contains(text(), "下一页")]/@href').extract_first()

        if next_page_url != "javascript:;":
            # 解析下一页, 指定dont_filter=True, 就可以实现增量爬虫了.
            yield scrapy.Request(url=next_page_url, dont_filter=True, callback=self.parse_job_list, meta=response.meta)

        # debug代码
        pass

    # 解析职位详情页
    def parse_job_detail(self, response):
        spider_name = self.name

        # 工作简介
        position_name = response.xpath('//div[contains(@class, "tHjob")]//h1/text()').extract_first().strip()
        salary_range = response.xpath('//div[contains(@class, "tHjob")]//strong/text()').extract_first()
        job_msg = response.xpath('//div[contains(@class, "tHjob")]//p[contains(@class, "msg")]/text()').extract()
        working_city = job_msg[0].strip() if len(job_msg)>=1 else ''
        experience_required = job_msg[1].strip() if len(job_msg)>=2 else ''
        education_required = job_msg[2].strip() if len(job_msg)>=3 else ''
        recruiting_num = job_msg[3].strip() if len(job_msg)>=4 else ''
        publish_time = job_msg[4].strip() if len(job_msg)>=5 else ''

        print(position_name, salary_range, working_city, experience_required, education_required, recruiting_num, publish_time, sep="\n")

        position_desc = '\n'.join(response.xpath('//div[contains(@class, "job_msg")]/p/text()').extract())
        position_label = ','.join([item.strip() for item in response.xpath('//p[@class="fp"][1]/a/text()').extract()])
        position_keyword = ','.join([item.strip() for item in response.xpath('//p[@class="fp"][2]/a/text()').extract()])
        position_tags = ','.join(set(position_keyword).union(set(position_keyword)))

        working_address = ''.join([item.strip() for item in response.xpath('//span[contains(text(), "上班地址：")]/../text()').extract()])

        company_intro = '\n'.join([item.strip() for item in response.xpath('//span[contains(text(), "公司信息")]/../../div[contains(@class, "tmsg")]/text()').extract()])

        print(position_desc, position_label, position_keyword, working_address, company_intro, sep="\n")

        # 公司信息
        company_job_url = response.xpath('//div[@class="tCompany_sidebar"]//div[@class="com_msg"]//a/@href').extract_first()
        company_name = response.xpath('//div[@class="tCompany_sidebar"]//div[@class="com_msg"]//p/text()').extract_first().strip()
        company_type = response.xpath('//span[@class="i_flag"]/../text()').extract_first()
        company_size = response.xpath('//span[@class="i_people"]/../text()').extract_first()
        company_industry = ','.join([item.strip() for item in response.xpath('//span[@class="i_trade"]/../a/text()').extract()])

        print(company_job_url, company_name, company_type, company_size, company_industry, sep="\n")

        job51_item = Job51SpiderItem(
            spider_name=self.name,  # 以爬虫名作为来源
            category_info = response.meta.get("category_info"),
            position_url = response.request.url,
            position_name = position_name,
            salary_range = salary_range,
            working_city = working_city,
            experience_required = experience_required,
            education_required = education_required,
            recruiting_num = recruiting_num,
            publish_time = publish_time,
            position_desc = position_desc,
            position_tags = position_tags,
            working_address = working_address,
            company_info = company_intro,
            company_job_url = company_job_url,
            company_name = company_name,
            company_type = company_type,
            company_size = company_size,
            company_field = company_industry
        )

        yield job51_item

    def parse_company_info(self, response):
        pass

    def parse_company_position(self, response):
        pass