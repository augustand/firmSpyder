# -*- coding: UTF-8 -*-

from scrapy.spiders import Spider
from mycrawler.items import BasicItem
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sets import Set
import scrapy
import logging


class FoscamSpider(Spider):
    name = "foscam"
    start_urls = ["http://www.foscam.com/index.php/Home/index/reg.html"]
    download_url = "http://www.foscam.com/download-center/firmware-downloads.html"
    timeout = 5
    trytimes = 3

    def parse(self, response):

        browser = webdriver.Firefox()
        browser.implicitly_wait(FoscamSpider.timeout)
        browser.set_page_load_timeout(FoscamSpider.timeout)

        t = FoscamSpider.trytimes
        while 1:
            try:
                try:
                    browser.get(response.url)
                except TimeoutException:
                    pass

                try:
                    login_button = WebDriverWait(browser, FoscamSpider.timeout).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@class='reg_click']/form/a")))
                except TimeoutException:
                    login_button = browser.find_element_by_xpath(
                        "//div[@class='reg_click']/form/a")
                try:
                    login_button.click()
                except TimeoutException:
                    pass

                try:
                    email = WebDriverWait(browser, FoscamSpider.timeout).until(EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='login_click']//input[@class='email']")))
                except TimeoutException:
                    login_button.click()
                    email = browser.find_element_by_xpath(
                        "//div[@class='login_click']//input[@class='email']")
                email.send_keys("test@iie.cn")
                email.submit()

                try:
                    success = WebDriverWait(browser, FoscamSpider.timeout).until(
                        EC.presence_of_element_located((By.ID, "tpl_main")))
                except TimeoutException:
                    pass
            except Exception, e:
                t -= 1
                logging.log(logging.WARNING, "Login failed, Try again(%d):%s",
                            FoscamSpider.trytimes - t, e.message)
                if t == 0:
                    logging.exception(e)
                    browser.quit()
                    return
            else:
                break
        t = FoscamSpider.trytimes
        items = Set()
        while 1:
            try:
                browser.get(FoscamSpider.download_url)
            except TimeoutException:
                pass
            try:
                main = WebDriverWait(browser, FoscamSpider.timeout).until(
                    EC.presence_of_element_located((By.ID, "main_right")))
            except TimeoutException:
                pass
            except Exception, e:
                t -= 1
                if t == 0:
                    logging.exception(e)
                    browser.quit()
                    return
            else:
                break

        span = main.find_element_by_xpath("span[position()=1]")
        table = main.find_elements_by_xpath("span[position()=1]/p")
        i = 1
        while i < len(table):
            item = BasicItem()
            item["Firm"] = "Foscam"
            item["Info"] = {"Series": "MJPEG"}
            item["Title"] = table[i].text.replace("\r", "").replace("\n", " ")
            item["Info"]["System Firmware Version"] = table[i + 1].text
            item["Info"]["WebUI Firmware Version"] = table[i + 2].text
            item["Descr"] = table[i + 4].text
            item["Link"] = table[
                i + 5].find_element_by_xpath("a").get_attribute("href").strip()
            item["Rawlink"] = item["Link"]
            item["Filename"] = item["Rawlink"].rsplit("/", 1).pop()
            items.add(item)
            i = i + 7
        logging.log(logging.INFO, "MJPEG finished,total items:%d", len(items))
        table = main.find_elements_by_xpath("span[position()=2]/p")
        i = 1
        while i < len(table):
            item = BasicItem()
            item["Firm"] = "Foscam"
            item["Info"] = {"Series": "H.264"}
            item["Title"] = table[i].text.replace("\r", "").replace("\n", " ")
            item["Info"]["Version"] = table[i + 1].text
            item["Link"] = table[
                i + 3].find_element_by_xpath("a").get_attribute("href").strip()
            item["Rawlink"] = item["Link"]
            item["Filename"] = item["Rawlink"].rsplit("/", 1).pop()
            items.add(item)
            i = i + 5
        logging.log(logging.INFO, "H.264 finished,total items:%d", len(items))
        browser.quit()
        return items
