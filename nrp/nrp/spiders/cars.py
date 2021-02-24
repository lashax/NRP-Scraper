import scrapy
from scrapy.http import HtmlResponse


class CarSpider(scrapy.Spider):
    name = 'cars'

    def start_requests(self):
        url = "https://nrp-performance.file-service.com/tuning-specs"
        yield scrapy.Request(url, callback=self.parse_main_page)

    def parse_main_page(self, response: HtmlResponse):
        car_types = response.xpath(
            "//select[@id='make_id']/option[position()>1]/text()").getall()
        for car in car_types:
            car = car.replace(' ', '-').replace('&', 'and')
            car = response.urljoin('/tuning-specs/' + car)
            yield scrapy.Request(car, callback=self.parse_models_page)

    def parse_models_page(self, response: HtmlResponse):
        # Last link follows to 'overview' page, so we don't need it
        models = response.xpath("//a[@class='btn btn--ghost border']"
                                "/@href").getall()[:-1]
        yield from response.follow_all(models,
                                       callback=self.parse_generations_page)

    def parse_generations_page(self, response: HtmlResponse):
        # Last two links are 'overview' and 'back' link, we don't need them
        generations = response.xpath("//a[@class='btn btn--ghost border']"
                                     "/@href").getall()[:-2]

        yield from response.follow_all(generations,
                                       callback=self.parse_engines_page)

    def parse_engines_page(self, response: HtmlResponse):
        # We don't need last three links for about same reason listed above
        engines = response.xpath("//a[@class='btn btn--ghost border']"
                                 "/@href").getall()[:-3]

        yield from response.follow_all(engines,
                                       callback=self.parse_details_page)

    def parse_details_page(self, response: HtmlResponse):
        stats = response.xpath("//div[contains(@class, "
                               "'ChiptuningComparison__number')]/"
                               "text()").getall()

        car_name = response.xpath("//div[@class='FileSpecs__improvements']"
                                  "/h1/text()").get()

        # Information contains lots of whitespace, so we filter that
        stats = [i.strip() for i in stats if i.strip()]
        bhp = f"Standard {stats[0]}, Chip tuning {stats[1]}, " \
              f"Difference {stats[2]}"
        torque = f"Standard {stats[3]}, Chip tuning {stats[4]}, " \
                 f"Difference {stats[5]}"

        more_stats = response.xpath("//div/span[2]/text()").getall()

        text = response.xpath("//div[@class='FileSpecs__text']/p/text()").get()
        list_items = response.xpath("//div[@class='FileSpecs__text']"
                                    "/ul/li/text()").getall()

        for list_item in list_items:
            text += '/n' + list_item

        yield {
            'Car': car_name,
            'BHP': bhp,
            'TORQUE': torque,
            'Method': more_stats[0],
            'Options': more_stats[1],
            'Details': text
        }
