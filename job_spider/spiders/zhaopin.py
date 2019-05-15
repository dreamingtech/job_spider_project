# -*- coding: utf-8 -*-
import scrapy


class ZhaopinSpider(scrapy.Spider):
    name = 'zhaopin'
    allowed_domains = ['zhaopin.com']
    start_urls = ['https://jobs.zhaopin.com/']

    def parse(self, response):
        # 对大分类进行分组
        main_cates = response.xpath('//div[@class="content-list"]')
        for main_cate in main_cates:
            main_cate_name = main_cate.xpath('./div/h2/text()').extract_first()
            sub_cates = main_cate.xpath('./div[@class="listcon"]/a')
            # 对次分类进行分组
            for sub_cate in sub_cates:
                sub_cate_name = sub_cate.xpath('./text()').extract_first()
                sub_cate_url = sub_cate.xpath('./@href').extract_first()
                sub_cate_url = response.urljoin(sub_cate_url)
                # 把分类信息组合成 "销售业务-销售代表" 的形式
                cate_info = "{}-{}".format(main_cate_name, sub_cate_name)
                meta = {"cate_info": cate_info}
                # 在列表页解析时设置dont_fileter=True, 这样, 在再次运行爬虫时就能再次提取信息, 实现增量爬虫
                # 把job_item使用meta传递过去,
                yield scrapy.Request(url=sub_cate_url, callback=self.parse_job_list, dont_filter=True, meta=meta)
                # 测试代码
                break
            break

    def parse_job_list(self, response):
        # 在解析时如果出现了404, 表示下一页不存在
        if response.status == "404":
            return
        positions = response.xpath('//div[contains(@class, "details_container")]')
        for position in positions:
            position_url = position.xpath('./span[@class="post"]/a/@href').extract_first()
            publish_time = position.xpath('./span[@class="release_time"]/text()').extract_first()
            from datetime import datetime
            publish_time = datetime.strptime(publish_time, "%y-%m-%d").date()
            meta = response.meta
            meta["publish_time"] = publish_time
            yield scrapy.Request(url=response.urljoin(position_url), callback=self.parse_job_detail, meta=meta)
            break

        next_page_url = response.xpath('//a[contains(text(), "下一页")]/@href').extract_first(default='')
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            # 解析下一页, 指定dont_filter=True, 就可以实现增量爬虫了.
            yield scrapy.Request(url=next_page_url, dont_filter=True, callback=self.parse_job_list, meta=response.meta)

    def parse_job_detail(self, response):
        meta = response.meta
        publish_time = meta.get("publish_time")
        come_from = self.name  # 以爬虫名作为来源
        cate_info = response.meta.get("cate_info")
        if response.status != 404:
            job_status = True
        else:
            job_status = False
        job_name = response.xpath('//h3[@class="summary-plane__title"]/text()').extract_first()
        job_url = response.url
        salary_range = response.xpath('//span[@class="summary-plane__salary"]/text()').extract_first()
        job_info = response.xpath('//ul[@class="summary-plane__info"]/li//text()').extract()

        if len(job_info) == 4:
            working_city = job_info[0]
            experience_required = job_info[1]
            education_required = job_info[2]
            position_num = job_info[3]
        else:
            working_city = ''
            experience_required = '1年'
            education_required = '本科'
            position_num = '1'
        job_tags = response.xpath('//div[@class="highlights__content"]/span/text()').extract()
        job_tags = ','.join(job_tags)
        recruiter_title = response.xpath('//h3[@class="manager__detail-name"]/text()').extract_first() if len(response.xpath('//h3[@class="manager__detail-name"]/text()'))>0 else ''
        job_descs = response.xpath('//div[@class="describtion"]//text()').extract()
        job_desc = "\n".join([job_desc.strip() for job_desc in job_descs])
        job_company_name = response.xpath('//a[@class="company__title"]/text()').extract_first()
        job_company_info_url = response.xpath('//a[@class="company__page-site"]/@href').extract_first()
        working_address = response.xpath('//span[@class="job-address__content-text"]/text()').extract_first()
        company_name = job_company_name
        company_scale = response.xpath('//button[@class="company__size"]/text()').extract_first()
        company_industry = response.xpath('//button[@class="company__industry"]/text()').extract_first()
        company_url = response.xpath('//a[@class="company__home-page"]/@href').extract_first()
        company_url = company_url.replace(r'/', '') if company_url.startswith('//') else company_url
        # zhaopin.com 独有字段
        company_intro = response.xpath('//div[@class="company__description"]/text()').extract_first()

        pass
