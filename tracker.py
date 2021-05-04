from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import sizes_conversion as conversion
from twocaptcha import TwoCaptcha
from selenium import webdriver
from bs4 import BeautifulSoup
import schedule as schedule
from time import sleep
import requests
import json
import re


class LuisaviaromaScraping:
    def __init__(self, driver):
        self.driver = driver
        self.SITE_URL = 'https://luisaviaroma.com/'

    def get_sizes(self, sku):
        self.sku = sku
        first_sizes_list = []
        second_sizes_list = []

        sku_list = sku.split('@')
        sku = sku_list[0]

        if len(sku_list) == 2:
            colour = sku_list[1].lower()
        else:
            colour = None

        self.driver.get(self.SITE_URL + sku)

        try:
            self.driver.find_element_by_xpath('//*[@id="exp--popup"]/button').click()
        except:
            pass

        if colour is not None:
            try:
                self.driver.find_element_by_xpath(
                    '//*[@id="root-body"]/div/div/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[1]/div[1]/div/div/span').click()
                sleep(2)
                colour_selector = self.driver.find_element_by_css_selector(
                    '#root-body > div > div > div._2CdjxFiLp1._3a-jZNt8IN > div._2AWtWi_Cud._3WUSoaaPMC._2Hm1RWYupR > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(2) > div > div')
                colours = colour_selector.find_elements_by_tag_name('span')
                for colour_ in colours:
                    if (colour_.text).lower() == colour:
                        colour_.click()
                        break

                sleep(2)
            except Exception as err:
                print(err)
                pass

        driver_wait(self.driver, 10, By.XPATH,
                    '//*[@id="root-body"]/div/div/div[2]/div[2]/div[2]/div[2]/div/div[1]/div[1]')
        try:
            self.driver.find_element_by_xpath(
                '//*[@id="root-body"]/div/div/div[2]/div[2]/div[2]/div[2]/div/div[1]/div[1]').click()
        except:
            check = self.check_captcha()
            if check is not None:
                self.get_sizes(self.sku)

            return None

        soup = create_soup(self.driver)

        sizes = soup.find_all('div', '_3kJMeU2j7k')
        if len(sizes) > 0:
            for size in sizes:
                size_json = json.loads(size['data-value'])
                first_sizes_list.append(size_json['SizeValue'])
                second_sizes_list.append(''.join(filter(str.isdigit, size_json['SizeCorrValue'])))
                object_type = self.get_object_type(soup)
                size_type = self.get_size_type(soup, size_number=1)

                json_data = {'object_type': object_type,
                             'size_type': size_type,
                             'sizes': first_sizes_list}

                new_json_data = conversion.convert_sizes(json_data)

                if new_json_data is None:
                    json_data = {'object_type': self.get_object_type(soup),
                                 'size_type': self.get_size_type(soup, size_number=2),
                                 'sizes': second_sizes_list}

                    new_json_data = conversion.convert_sizes(json_data)

            return new_json_data

        else:
            try:
                size_value = soup.find_all('div', '_1607_GmTdI')[1].findChild('div').text
            except IndexError:
                return

            if 'IT' in size_value:
                size_type = 'IT'

            elif 'UK' in size_value:
                size_type = 'UK'

            elif 'US' in size_value:
                size_type = 'USA'

            elif (
                    'XXS' in size_value or 'XS' in size_value or 'S' in size_value or 'M' in size_value or 'L' in size_value
                    or 'XL' in size_value or 'XXL' in size_value or 'XXXL' in size_value or '4XL' in size_value or '5XL' in size_value):
                size_type = 'S/M/L'

            else:
                size_type = 'None'

            if size_value is not None:
                num_filter = filter(str.isdigit, size_value)
                size_value = ''.join(num_filter)

            first_sizes_list.append(size_value)
            object_type = self.get_object_type(soup)
            json_data = {'object_type': object_type,
                         'size_type': size_type,
                         'sizes': first_sizes_list}

            new_json_data = conversion.convert_sizes(json_data)

            return new_json_data

    '''Clothing, shoes, bags etc'''

    def get_object_type(self, soup):
        objects = soup.find_all('span', {'itemprop': 'name'})
        if len(objects) > 0:
            return objects[1].string

    '''XML, IT, UK, USA, JAPAN etc'''

    def get_size_type(self, soup, size_number):
        return soup.find_all('span', '_3IODCKFLTa')[size_number - 1].string

    def check_captcha(self):
        self.CAPTCHA_KEY = 'ef66bec6deb8dce76dee29735d99ad49'
        soup = create_soup(self.driver)
        captcha_tag = soup.find('div', 'g-recaptcha')
        if captcha_tag is not None:
            self.bypass_captcha(captcha_tag)
            return 'Bypassed'

        return None

    def bypass_captcha(self, captcha_tag):
        # Bypassing ReCaptcha
        sitekey = captcha_tag['data-sitekey']
        url = self.driver.current_url
        solver = TwoCaptcha(self.CAPTCHA_KEY)
        result = solver.recaptcha(sitekey=sitekey,
                                  url=url,
                                  version=2)
        print(result['code'])
        self.driver.execute_script(
            'document.getElementById("g-recaptcha-response").innerHTML="{}";'.format(result['code']))
        sleep(3)
        self.driver.execute_script('submitForm()')
        sleep(10)


class AsosScraping:
    def __init__(self, driver):
        self.driver = driver
        self.driver.maximize_window()
        self.SITE_URL = 'https://asos.com/'

    def get_sizes(self, sku):
        self.driver.get(self.SITE_URL)
        try:
            self.driver.find_element_by_xpath('//*[@id="chrome-header"]/header/div[1]/div/div/button').click()
        except:
            pass
        self.set_ireland()
        self.driver.find_element_by_xpath('//*[@id="chrome-search"]').send_keys(sku)
        self.driver.find_element_by_xpath('//*[@id="chrome-search"]').send_keys(Keys.ENTER)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#main-size-select-0 > option:nth-child(2)"))
            )
        except:
            print('No size selector')

        try:
            self.driver.find_element_by_xpath('//*[@id="chrome-welcome-mat"]/div/div/button/span').click()
        except:
            pass

        self.sizes = self.scrape_sizes()
        self.converted_sizes = conversion.convert_sizes(self.sizes)

        return self.converted_sizes

    def set_ireland(self):
        driver_wait(self.driver, 10, By.XPATH, '//*[@id="chrome-header"]/header/div[2]/div/ul/li[3]/div/button')
        self.driver.find_element_by_xpath('//*[@id="chrome-header"]/header/div[2]/div/ul/li[3]/div/button').click()
        sleep(0.5)
        select = Select(self.driver.find_element_by_xpath('//*[@id="country"]'))
        select.select_by_visible_text('Ireland, Republic of')
        driver_wait(self.driver, 10, By.XPATH,
                    '//*[@id="chrome-modal-container"]/div/div[2]/div/div/section/form/div[3]/button')
        self.driver.find_element_by_xpath(
            '//*[@id="chrome-modal-container"]/div/div[2]/div/div/section/form/div[3]/button').click()
        sleep(0.5)
        self.driver.get(self.SITE_URL)

    def scrape_sizes(self):
        self.sizes_list = []
        soup = create_soup(self.driver)
        sizes_selector = soup.find('select', {'data-id': 'sizeSelect'})
        if sizes_selector is not None:
            sizes_tags = sizes_selector.findChildren('option')
            if sizes_tags is not None:
                for size in sizes_tags:
                    try:
                        if size.text == 'Please select' or size['disabled'] == '':
                            continue
                    except:
                        self.sizes_list.append((size.string).split(' - ')[0])

                    object_type = self.get_object_type()
                    size_type = self.get_size_type()
                    if not size_type == 'S/M/L':
                        sizes_value = self.get_sizes_value()
                    else:
                        sizes_value = self.sizes_list

        return {
            'object_type': object_type,
            'size_type': size_type,
            'sizes': sizes_value
        }

    def get_object_type(self):
        shoes_types = ['boot', 'sandal', 'shoe', 'slider', 'flops', 'slipper', 'trainers', 'heels']
        soup = create_soup(self.driver)
        object_title = soup.find('title').text
        for shoes_type in shoes_types:
            if shoes_type in object_title:
                return 'Shoes'

        return 'Clothing'

    def get_sizes_value(self):
        sizes_value = []
        for size in self.sizes_list:
            try:
                sizes_value.append(re.findall(r'\d+\.?\d?', size)[0])
            except:
                continue

        return sizes_value

    def get_size_type(self):
        size_value = self.sizes_list[0]

        if 'IT' in size_value:
            return 'IT'

        elif 'UK' in size_value:
            return 'UK'

        elif 'US' in size_value:
            return 'USA'

        elif (
                'XXS' in size_value or '2XS' in size_value or 'XS' in size_value or 'S' in size_value or 'M' in size_value or 'L' in size_value
                or 'XL' in size_value or 'XXL' in size_value or 'XXXL' in size_value or '4XL' in size_value or '5XL' in size_value):
            return 'S/M/L'

        else:
            return None

    # todo remove
    def create_href_list(self):
        item_list = []
        items = ''
        self.driver.get(
            'https://www.asos.com/men/designer/cat/?cid=27111&nlid=mw%7Cclothing%7Cshop%20by%20product%7Cdesigner')
        while True:
            try:
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                self.driver.find_element_by_xpath('//*[@id="plp"]/div/div/div[2]/div/a').click()
                sleep(1)
            except:
                break

        soup = create_soup(self.driver)
        clothes = soup.find_all('a', '_3TqU78D')

        for item in clothes:
            item_list.append(item['href'])

        for item in item_list:
            items += item + ','

        with open('clothes_asos.txt', 'w') as f:
            f.write(items)


class ShopifyAPI:
    def __init__(self):
        self.ADMIN_URL = 'https://51e223c4cfbdc43f649baa8121d6fe05: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@bunkerclothing.myshopify.com'

    def get_products_count(self):
        try:
            product = requests.get(self.ADMIN_URL + '/admin/api/2021-04/products/count.json').json()

            return product['count']

        except:
            return None

    def get_page_info_id(self, headers, indent):
        try:
            info_ids = re.findall(r'page_info=([^>]+)', headers['link'])
        except KeyError:
            return None

        return info_ids[indent]

    def get_products_json(self):
        request = requests.get(self.ADMIN_URL + '/admin/api/2021-04/products.json?limit=250')
        page_info = self.get_page_info_id(request.headers, indent=0)
        if page_info is None:
            return request.json()

        while True:
            try:
                request = requests.get(
                    self.ADMIN_URL + '/admin/api/2021-04/products.json?limit=250&page_info={}'.format(page_info))
                page_info = self.get_page_info_id(request.headers, indent=1)
            except:
                break

        return request.json()

    def get_product_json(self, id):
        return requests.get(self.ADMIN_URL + '/admin/api/2021-04/products/{}.json'.format(id)).json()

    def get_all_SKU_products(self):
        counter = 1
        products_list = []
        # todo fix func
        products = self.get_products_json()
        for product in products['products']:
            for variant in product['variants']:
                sku = variant['sku']

                counter += 1

                if sku is not None:
                    sku = variant['sku'].replace(' ', '')

                if str(sku) != 'None' and sku != '':
                    products_list.append(product['id'])
                    break

        return products_list

    def get_SKU(self, product_id):
        product = self.get_product_json(product_id)

        return product['product']['variants'][0]['sku']

    def get_sizes_list(self, product_id):
        sizes_list = []
        product = self.get_product_json(product_id)
        for variant in product['product']['variants']:
            sizes_list.append(variant['title'])

        return sizes_list

    def update_product_variants(self, product_id, set_list, remove_list, create_list):
        product = self.get_product_json(product_id)

        if len(set_list) > 0:
            self.set_variant_checkbox(product, set_list)

        if len(remove_list) > 0:
            self.remove_variant_checkbox(product, remove_list)

        if len(create_list) > 0:
            self.create_variant_checkbox(product, product_id, create_list)

    def remove_variant_checkbox(self, product, remove_list):
        for variant in product['product']['variants']:
            if variant['title'] in remove_list:
                variant_id = variant['id']
            else:
                continue

            if variant_id is not None:
                put_data = {
                    "Content-Type": "application/json",
                    "variant": {
                        "id": int(variant_id),
                        "inventory_policy": "deny"
                    }
                }

                requests.put(self.ADMIN_URL + '/admin/api/2021-04/variants/{}.json'.format(str(variant_id)),
                             json=put_data)

    def set_variant_checkbox(self, product, set_list):
        for variant in product['product']['variants']:
            if variant['title'] in set_list:
                variant_id = variant['id']
            else:
                continue

            if variant_id is not None:
                put_data = {
                    "Content-Type": "application/json",
                    "variant": {
                        "id": int(variant_id),
                        "inventory_policy": "continue"
                    }
                }
                requests.put(self.ADMIN_URL + '/admin/api/2021-04/variants/{}.json'.format(str(variant_id)),
                             json=put_data)

    def create_variant_checkbox(self, product, product_id, create_list):
        sizes = create_list
        price = product['product']['variants'][0]['price']
        sku = self.get_SKU(product_id)
        for size in sizes:
            post_data = {
                "variant": {
                    "option1": size,
                    "sku": sku,
                    "price": price,
                    "inventory_policy": "continue"
                }
            }

            requests.post(self.ADMIN_URL + '/admin/api/2021-04/products/{}/variants.json'.format(product_id),
                          json=post_data)


class Tracker:
    def __init__(self):
        self.api = ShopifyAPI()

    def track_clothing(self):
        driver = create_driver()
        sku_products = self.api.get_all_SKU_products()
        for sku_product in sku_products:
            bunker_sizes = self.api.get_sizes_list(sku_product)
            sku = self.api.get_SKU(sku_product)
            print('Tracking SKU: ' + sku)
            if '-' in sku:
                target_tracker = LuisaviaromaScraping(driver)

                try:
                    target_sizes = target_tracker.get_sizes(sku)

                except Exception as err:
                    print(err)
                    continue
            else:
                target_tracker = AsosScraping(driver)

                try:
                    target_sizes = target_tracker.get_sizes(sku)

                except Exception as err:
                    print(err)
                    continue

            if target_sizes is not None and len(target_sizes) != 0:
                target_sizes = convert_to_bunker_format(target_sizes)
                self.update_product(sku_product, bunker_sizes, target_sizes)
                print('Tracked Success')
            else:
                continue

        driver.quit()

    def update_product(self, product_id, bunker_sizes, target_sizes):
        set_checkbox_sizes_list = []
        remove_checkbox_sizes_list = []
        create_sizes_list = []
        for target_size in target_sizes:
            if target_size in bunker_sizes:
                set_checkbox_sizes_list.append(target_size)
            else:
                create_sizes_list.append(target_size)

        for bunker_size in bunker_sizes:
            if not bunker_size in set_checkbox_sizes_list:
                remove_checkbox_sizes_list.append(bunker_size)
        self.api.update_product_variants(product_id, set_checkbox_sizes_list, remove_checkbox_sizes_list,
                                         create_sizes_list)


def convert_to_bunker_format(sizes_json):
    sizes = sizes_json['sizes']
    if sizes_json['size_type'] == "UK":
        i = 0
        for size in sizes:
            sizes[i] = 'UK' + str(size)
            i += 1

        return sizes

    elif sizes_json['size_type'] == 'S/M/L':
        return sizes

    elif sizes_json['size_type'] == 'CM':
        return sizes


def create_soup(driver):
    return BeautifulSoup(driver.page_source, 'lxml')


def create_xpath(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
            )
        )
        child = parent
        components.reverse()
    return '/%s' % '/'.join(components)


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')

    return webdriver.Chrome(options=options)


def driver_wait(driver, time, chosen_type, text):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((chosen_type, text))
        )
    except:
        print('Timeout {} seconds: {} : {}'.format(str(time), chosen_type, text))


def track():
    tracker = Tracker()
    tracker.track_clothing()


if __name__ == '__main__':
    schedule.every().day.at("08:00").do(track)
    schedule.every().day.at("09:00").do(track)
    schedule.every().day.at("10:00").do(track)
    schedule.every().day.at("11:00").do(track)
    schedule.every().day.at("12:00").do(track)
    schedule.every().day.at("14:00").do(track)
    schedule.every().day.at("15:00").do(track)
    schedule.every().day.at("16:00").do(track)
    schedule.every().day.at("17:00").do(track)
    schedule.every().day.at("18:00").do(track)
    schedule.every().day.at("19:00").do(track)
    schedule.every().day.at("20:00").do(track)
    schedule.every().day.at("21:00").do(track)
    schedule.every().day.at("22:00").do(track)
    schedule.every().day.at("23:59").do(track)

    while True:
        schedule.run_pending()
        sleep(1)
