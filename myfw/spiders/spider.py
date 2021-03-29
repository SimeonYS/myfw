import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import MyfwItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class MyfwSpider(scrapy.Spider):
	name = 'myfw'
	start_urls = ['https://myfw.com/articles/page/1/']
	page = 1

	def parse(self, response):
		articles = response.xpath('//div[@class="blog-index-post-copy"]')
		for article in articles:
			date = article.xpath('.//h5/text()').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		# next_page_button = response.xpath('//li[@class="next-posts"]/a/@href').get()
		next_page = f'https://myfw.com/articles/page/{self.page}/'
		# if next_page_button:
		if articles:
			self.page += 1
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="blog-page-content"]//text()[not (ancestor::div[@class="icons  module"] or ancestor::h4)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=MyfwItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
