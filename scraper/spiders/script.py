import re
import scrapy
from abc import ABC
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ScrapySpider(CrawlSpider, ABC):
    name = 'get_data'
    allowed_domains = ['contest-646508-5umjfyjn4a-ue.a.run.app']
    start_urls = ['https://contest-646508-5umjfyjn4a-ue.a.run.app/']

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        if response.css('#uuid ::text').get():

            # fix image_id
            image_id = response.css('#2 img ::attr("src")').get()
            if image_id:
                image_id = image_id.split('/')[-1].split('.')[0].split('_')[-1]
            else:
                image_id = re.findall('const iid = \'[^\']+', response.body.decode('utf-8'))
                if len(image_id) > 0:
                    image_id = image_id[0].split("'")[-1]
                else:
                    image_id = None

            item = {
                'item_id': response.css('#uuid ::text').get(),
                'name': response.css('#2 h2 ::text').get(),
                'image_id': image_id,
                'flavor': response.css('#2 p:contains("Flavor") span ::text').get(),
            }

            # fix flavor
            flavor = response.css('#2 p:contains("Flavor") span ::attr("data-flavor")').get()
            if flavor:
                if flavor[0] == '/':
                    flavor = response.urljoin(flavor)
                yield scrapy.Request(url=flavor,
                                     callback=self.parse_flavor,
                                     errback=self.parse_flavor_error,
                                     dont_filter=True,
                                     meta={'item': item})
            else:
                yield item

    def parse_flavor(self, response):
        item = response.meta.get('item')
        item['flavor'] = response.json().get('value')
        yield item

    def parse_flavor_error(self, response):
        item = response.meta.get('item')
        yield item
