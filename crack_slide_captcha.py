# coding:utf8
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
try:
    from Pillow import Image as image
except ImportError:
    from PIL import Image as image
import time,re, random
import requests
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class CrackSlide(object):

    def __init__(self):
        self.agent = 'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0'
        self.headers = {'User-Agent': self.agent}
        self.is_display = True

    def get_browser(self):
        if self.is_display == True:
            self.browser = webdriver.Chrome()
        else:
            agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27"
            dcap = DesiredCapabilities.PHANTOMJS
            dcap['phantomjs.page.settings.userAgent'] = agent
            self.browser = webdriver.PhantomJS(desired_capabilities=dcap)
        self.browser.get("http://www.gsxt.gov.cn/")
        time.sleep(1)

    def exec_crack(self, text=u'中国移动', is_display=True):
        self.is_display = is_display
        self.get_browser()
        self.input_text(text=text)
        self.submit()
        self.waiting_element()
        image1 = self.get_image("//div[@class='gt_cut_bg gt_show']/div")
        image2 = self.get_image("//div[@class='gt_cut_fullbg gt_show']/div")
        offset = self.get_diff_location(image1, image2)
        track_list = self.get_track(offset)
        self.drag_and_drop(track_list, offset)
        time.sleep(2)
        content =  self.browser.page_source
        self.browser.delete_all_cookies()
        self.browser.quit()
        return content

    def drag_and_drop(self, track_list, offset):
        element = self.browser.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
        location = element.location
        y = location['y']
        ActionChains(self.browser).click_and_hold(on_element=element).perform()
        num = 30
        count = 0

        for track in track_list:

            ActionChains(self.browser).move_to_element_with_offset(to_element=element, xoffset=22,
                                                             yoffset=random.randint(380, 390)).perform()
            time.sleep(0.01)

        for track in track_list:

            ActionChains(self.browser).move_to_element_with_offset(to_element=element, xoffset=-22,
                                                             yoffset=random.randint(380, 390)).perform()
            time.sleep(0.01)

        for track in track_list:

            ActionChains(self.browser).move_to_element_with_offset(to_element=element, xoffset=track + 22,
                                                             yoffset=random.randint(380, 390)).perform()
            count += 1
            if count < num:
                time.sleep(0.01)
            else:
                time.sleep(0.1)
        for i in xrange(5):
            ActionChains(self.browser).move_to_element_with_offset(to_element=element, xoffset=21, yoffset=random.randint(380, 390)).perform()
            time.sleep(0.1)
        ActionChains(self.browser).release(on_element=element).perform()

    def input_text(self, text, el_id='keyword'):
        input_el = self.browser.find_element_by_id(el_id)
        input_el.click()
        input_el.send_keys(text)
        time.sleep(2)

    def submit(self, el_class='f18'):
        submit_el = self.browser.find_element_by_class_name(el_class)
        submit_el.click()
        time.sleep(2)

    def get_image(self, img_xpath):
        background_images = self.browser.find_elements_by_xpath(img_xpath)
        location_list = []
        imageurl = ''
        if self.is_display == True:
            for background_image in background_images:
                location = {}
                location['x'] = int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                             background_image.get_attribute('style'))[0][1])
                location['y'] = int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                             background_image.get_attribute('style'))[0][2])
                imageurl = re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                      background_image.get_attribute('style'))[0][0]
                location_list.append(location)
        else:
            for background_image in background_images:
                location = {}
                location['x'] = int(re.findall("background-image: url\((.*)\); background-position: (.*)px (.*)px;",
                                               background_image.get_attribute('style'))[0][1])
                location['y'] = int(re.findall("background-image: url\((.*)\); background-position: (.*)px (.*)px;",
                                               background_image.get_attribute('style'))[0][2])
                imageurl = re.findall("background-image: url\((.*)\); background-position: (.*)px (.*)px;",
                                      background_image.get_attribute('style'))[0][0]
                location_list.append(location)

        imageurl = imageurl.replace("webp", "jpg")

        session = requests.session()
        response = session.get(imageurl, headers=self.headers, verify=False)
        image_mix = StringIO(response.content)
        image = self.get_merge_image(image_mix, location_list)
        return image


    def get_merge_image(self, image_mix, location_list):
        im = image.open(image_mix)
        im_list_upper=[]
        im_list_down=[]
        for location in location_list:
            if location['y']==-58:
                im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x'])+10, 166)))
            if location['y']==0:
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x'])+10, 58)))
        new_im = image.new('RGB', (260,116))
        x_offset = 0
        for im in im_list_upper:
            new_im.paste(im, (x_offset,0))
            x_offset += im.size[0]
        x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset,58))
            x_offset += im.size[0]
        return new_im

    def is_similar(self, image1, image2, x, y):
        pixel1 = image1.getpixel((x, y))
        pixel2 = image2.getpixel((x, y))
        for i in range(0, 3):
            if abs(pixel1[i] - pixel2[i]) >= 50:
                return False
        return True

    def get_diff_location(self, image1, image2):
        for i in range(0, 260):
            for j in range(0, 116):
                if self.is_similar(image1, image2, i, j) == False:
                    return i

    def get_track(self, offset):
        list = []
        x = random.randint(3, 8)
        while offset - x >= 5:
            list.append(x)
            offset = offset - x
            x = random.randint(2, 3)
        for i in range(offset):
            list.append(1)
        return list

    def waiting_element(self):
        WebDriverWait(self.browser, 30).until(
            lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']").is_displayed())
        WebDriverWait(self.browser, 30).until(
            lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_cut_bg gt_show']").is_displayed())
        WebDriverWait(self.browser, 30).until(
            lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_cut_fullbg gt_show']").is_displayed())

if __name__ == "__main__":
    crack = CrackSlide()
    content = crack.exec_crack(is_display=True)