# -*- coding: utf-8 -*-
import scrapy
from job_spider.items import LagouSpiderItem

class LagouSpider(scrapy.Spider):
    name = 'lagou'
    allowed_domains = ['lagou.com']
    start_urls = ['https://www.lagou.com/']


    # 从主页主导航中解析出职位列表页的url
    def parse(self, response):
        main_cates = response.xpath('//div[@class="menu_box"]')
        # 对主分类进行分组
        for main_cate in main_cates:
            main_cate_name = main_cate.xpath('.//div[@class="category-list"]/h2/text()').extract_first().strip()
            # sub_cates取到dl, 否则次分类无法提取完整
            sub_cates = main_cate.xpath('.//div[contains(@class, "menu_sub")]/dl')
            # 对次分类进行分组
            for sub_cate in sub_cates:
                sub_cate_name = sub_cate.xpath('./dt/span/text()').extract_first()
                cates = sub_cate.xpath('./dd/a')
                # 对一个具体的职位类别进行分组
                for cate in cates:
                    cate_name = cate.xpath('./text()').extract_first()
                    cate_url = cate.xpath('./@href').extract_first()
                    print("*"*50)
                    print(main_cate_name)
                    print(sub_cate_name)
                    print(cate_name)
                    print(cate_url)
                    print("*"*50)
                    # 把分类信息组合成 "销售业务-销售代表" 的形式
                    cate_info = "{}-{}-{}".format(main_cate_name, sub_cate_name, cate_name)
                    meta = {"cate_info": cate_info}
                    # meta = {"main_cate_name": main_cate_name, "sub_cate_name": sub_cate_name, "cate_name": cate_name}
                    # 在列表页解析时设置dont_fileter=True, 这样, 在再次运行爬虫时就能再次提取信息, 实现增量爬虫
                    # 把job_item使用meta传递过去,
                    yield scrapy.Request(url=cate_url, callback=self.parse_job_list, dont_filter=True, meta=meta)
                    # 测试代码
            #         break
            #     break
            # break

    # 从列表页中提取详情页url
    def parse_job_list(self, response):
        positions = response.xpath('//ul[@class="item_con_list"]/li')
        for position in positions:
            position_url = position.xpath('.//a[@class="position_link"]/@href').extract_first()
            yield scrapy.Request(url=position_url, callback=self.parse_job_detail, meta=response.meta)
            # 测试代码
            break
        # 提取出下一页的url
        next_page_url = response.xpath('//div[@class="pager_container"]/a[contains(text(), "下一页")]/@href').extract_first()

        if next_page_url != "javascript:;":
            # 解析下一页, 指定dont_filter=True, 就可以实现增量爬虫了.
            yield scrapy.Request(url=next_page_url, dont_filter=True, callback=self.parse_job_list, meta=response.meta)
            # debug代码
            pass
        # debug代码
        pass

    # 解析职位详情页
    def parse_job_detail(self, response):
        job_name = response.xpath('//div[@class="job-name"]/span[@class="name"]/text()').extract_first()

        # 工作简介
        salary_range = response.xpath('//dd[@class="job_request"]/p/span[1]/text()').extract_first().replace('/','').strip()
        working_city = response.xpath('//dd[@class="job_request"]/p/span[2]/text()').extract_first().replace('/','').strip()
        experience_required = response.xpath('//dd[@class="job_request"]/p/span[3]/text()').extract_first().replace('/','').strip()
        education_required = response.xpath('//dd[@class="job_request"]/p/span[4]/text()').extract_first().replace('/','').strip()
        job_type = response.xpath('//dd[@class="job_request"]/p/span[5]/text()').extract_first().replace('/','').strip()
        position_label = ','.join(response.xpath('//ul[contains(@class, "position-label")]/li/text()').extract())
        publish_time = response.xpath('//p[@class="publish_time"]/text()').extract_first().split('\xa0')[0]

        # 工作详情
        job_tags = response.xpath('//dd[@class="job-advantage"]/p/text()').extract_first()
        job_desc = '\n'.join(response.xpath('//div[@class="job-detail"]/p//text()').extract()).replace('\xa0','')

        # 工作详细地址
        working_city_temp = response.xpath('//div[@class="work_addr"]/a[1]/text()').extract_first()
        working_district_temp = response.xpath('//div[@class="work_addr"]/a[2]/text()').extract_first()
        working_address_temp = ''.join(response.xpath('//div[@class="work_addr"]/text()').extract()).replace('-','').strip()
        working_address = "{}-{}-{}".format(working_city_temp, working_district_temp, working_address_temp)

        # 公司信息
        company_lagou_url = response.xpath('//dl[@class="job_company"]/dt/a/@href').extract_first()
        company_name = response.xpath('//dl[@class="job_company"]/dt/a/div/h2/text()').extract_first().strip()
        company_field = ''.join(response.xpath('//ul[@class="c_feature"]/li[1]/text()').extract()).strip()
        financing_status = ''.join(response.xpath('//ul[@class="c_feature"]/li[2]/text()').extract()).strip()
        company_size = ''.join(response.xpath('//ul[@class="c_feature"]/li[3]/text()').extract()).strip()
        company_url = ''.join(response.xpath('//ul[@class="c_feature"]/li[4]//a/@href').extract()).strip()

        print("*"*50)
        print(job_name, salary_range, working_city, experience_required, education_required, job_type, position_label, publish_time, sep='\n')
        print("*"*50)
        print(job_advantage, job_detail, working_address, sep='\n')
        print("*"*50)
        print(company_lagou_url, company_name, company_field, financing_status, company_size, company_url, sep='\n')
        print("*"*50)

        lagou_item = LagouSpiderItem(
            come_from=self.name,  # 以爬虫名作为来源
            cate_info = response.meta.get("cate_info"),
            job_name = job_name,
            salary_range = salary_range,
            working_city = working_city,
            experience_required = experience_required,
            education_required = education_required,
            job_type = job_type,
            position_label = position_label,
            publish_time = publish_time,
            job_tags = job_tags,
            job_desc = job_desc,
            working_address = working_address,
            company_lagou_url = company_lagou_url,
            company_name = company_name,
            company_field = company_field,
            financing_status = financing_status,
            company_size = company_size,
            company_url = company_url
        )

        yield lagou_item

    def parse_company_info(self, response):
        pass

    def parse_company_position(self, response):
        pass

    def campus_recruitment_position(self, response):
        """校招职位"""
        pass