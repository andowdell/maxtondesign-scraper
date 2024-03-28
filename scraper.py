import requests
import re
import json
from lxml import html

CATEGORY_PATTERN = r'{[^{}]*"category_id":"(\d+)","name":"([^"]+)","href":"([^"]+)"[^{}]+}'

class Scraper():
    def __init__(self) -> None:
        self.session = requests.Session()
        self.categories = []
        pass

    def load_categories(self):
        categories = []
        response = self.session.get('https://www.maxtondesign.co.uk/')
        matches = re.findall(CATEGORY_PATTERN, response.text)
        for match in matches:
            if match[1] == 'Body Kits':
                continue
            categories.append({'id': match[0], 'name': match[1], 'url': match[2].replace('\\/', '/')})
        return categories
    
    def get_products(self, category, page):
        resp = self.session.get('https://www.maxtondesign.co.uk/index.php', timeout=3000, params={
            'route': 'product/product/getProducts', 
            'category_id': category['id'],
            'sort': 'default',
            'page': f'{page}',
            'filter_category_id': '',
            'filter_filter': '',
        })
        results = json.loads(resp.text)
        if results['products'] and len(results['products']) > 0:
            return results['products']
        return None

    def load_products(self, category):
        page = 1
        while True:
            print(page)
            products = self.get_products(category, page)
            if products is None:
                break
            for product in products:
                print('$$$ PRODUCT : ', product['name'])
                product['Category'] = category['name']
                product['Title'] = product['name']
                self.get_product_info(product)
            page += 1
    
    def get_product_info(self, product):
        resp = self.session.get(product['href'], timeout=3000)
        tree = html.fromstring(resp.text)
        elements = tree.xpath('//table[@class="table table--clean"]/tr')
        for element in elements:
            td_elements = element.xpath('./td')
            key = td_elements[0].text_content().strip().replace(':', '')
            value = td_elements[1].text_content().strip()
            product[key] = value
        desc = tree.xpath("//div[@id = 'accordion-data1']")
        product['Description'] = html.tostring(desc[0])

    def start(self):
        categories = self.load_categories()
        for category in categories:
            print("### CATEGORY : ", category['id'], ':', category['name'], )
            self.load_products(category)



def main():
    scraper = Scraper()
    scraper.start()
    
if __name__ == "__main__":
    main()