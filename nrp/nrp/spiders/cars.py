import scrapy
from scrapy.http import HtmlResponse


class CarsSpider(scrapy.Spider):
    name = 'car'

    def start_requests(self):
        url = "https://nrp-performance.file-service.com/tuning-specs/lamborghini-tractors"
        yield scrapy.Request(url, callback=self.parse_first_page)

    def parse_first_page(self, response: HtmlResponse):
        car_types = response.xpath(
            "//select[@id='make_id']/option[position()>1]/text()").getall()
        for car in car_types:
            car = car.replace(' ', '-').replace('&', 'and')
            car = response.urljoin('/tuning-specs/' + car)
            yield scrapy.Request(car, callback=self.parse_second_page)

    def parse_second_page(self, response):
        pass