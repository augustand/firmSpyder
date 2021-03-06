# -*- coding: UTF-8 -*-

import logging
import scrapy
from scrapy.spiders import Spider
from mycrawler.items import BasicItem
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sets import Set

from ..dbUtil import url_items


class AbbSpider(Spider):
    name = "abb"
    # url_items(name)
    start_urls = [
        "http://www.abb.com/AbbLibrary/DownloadCenter/default.aspx?showresultstab=true&CategoryID=9AAC113401&DocumentKind=Manual&Documentlanguage=zh&DisplayLanguage=en#&&/wEXAQUDa2V5BYMBM8KwOUFBQzE3NzAzM8KxwrHCsVNvZnR3YXJlwrHCsVTCscKxNMKxwrEyOcKxQ07CscKxMsKxVMKxMMKxwrEwwrExwrEyMMKxMjDCsTHCscKxwrHCscKxOUFBQzExMzQwMcKxwrHCscKxMTHCscKxwrHCsTY4wrHCsTDCsUNOwrHCsTB9cE7o9jBIVfA/PfxkFN8NH2/JJQ==",
    ]

    timeout = 5
    trytimes = 3

    def parse(self, response):

        browser = webdriver.Firefox(None, None, 15)
        browser.implicitly_wait(AbbSpider.timeout)
        browser.set_page_load_timeout(AbbSpider.timeout)

        t = AbbSpider.trytimes
        while 1:
            try:
                browser.get(AbbSpider.start_urls[0])
            except TimeoutException:
                pass
            try:
                print "0\n\n\n\n"
                WebDriverWait(browser, AbbSpider.timeout, 1).until(lambda x: x.find_element_by_id(
                "ctl00_csMainRegion_csContentRegion_MainArea_paging_pagingUl_span2N_2N").text == "Next")
                    #"//div[@class='boxfilter']/div/p[@class='value']"
                print "\n\n\n\n"
            except Exception, e:
                print e
                try:
                    WebDriverWait(browser, AbbSpider.timeout).until(lambda x: x.find_element_by_id(
                "ctl00_csMainRegion_csContentRegion_MainArea_paging_pagingUl_span2N_2N").text == "Next")
                    print "2\n\n\n\n"
                except TimeoutException, e:
                    print e
                    t -= 1
                    logging.log(
                        logging.WARNING, "Switching to PLC page failed(%d)", AbbSpider.trytimes - t)
                    if t == 0:
                        print e
                        browser.quit()
                        return
            else:
                break

        page = "0"
        t = AbbSpider.trytimes
        while 1:
            try:
                WebDriverWait(browser, AbbSpider.timeout).until(lambda x: page != (
                    x.find_element_by_xpath("//ul[@class='paging']/li/span[@class='current']").text))
            except WebDriverException, e:
                t -= 1
                logging.log(
                    logging.WARNING, "Going to next page failed(%d)", AbbSpider.trytimes - t)
                if t == 0:
                    browser.quit()
                    raise e
                continue
            page = browser.find_element_by_xpath(
                "//ul[@class='paging']/li/span[@class='current']").text
            t = AbbSpider.trytimes
            while 1:
                browser.execute_script(
                    "javascript:__doPostBack('ctl00$csMainRegion$csContentRegion$MainArea$inner$expcolall','')")
                try:
                    WebDriverWait(browser, AbbSpider.timeout).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "share")))
                except TimeoutException:
                    t -= 1
                    logging.log(
                        logging.WARNING, "Expanding all details failed(%d)", AbbSpider.trytimes - t)
                    if t == 0:
                        browser.quit()
                        raise TimeoutException(
                            "Detail for items cannot be expanded")
                else:
                    break

            t = AbbSpider.trytimes

            rows = browser.find_elements_by_xpath(
                "//div[@id='ctl00_csMainRegion_csContentRegion_MainArea_result']/div/div/div/div[@class='details']")
            for tr in rows:
                item = BasicItem()
                item["Info"] = {}
                item["Firm"] = "Abb"
                item["Title"] = tr.find_element_by_class_name("title").text
                item["Link"] = tr.find_element_by_xpath(
                    "div[@class='title']/span/a").get_attribute("href")
                item["Rawlink"] = item["Link"].split("&", 1)[0]
                pros = tr.find_elements_by_xpath(
                    "div[@class='properties']/span[@class='property']")
                vals = tr.find_elements_by_xpath(
                    "div[@class='properties']/span[@class='value']")
                i = 0
                while i < len(pros):
                    key = pros[i].text.rsplit(":", 1)[0]
                    if key == "Summary":
                        item["Descr"] = vals[i].text
                    elif key == "Doc No":
                        item["Filename"] = vals[i].text
                    elif key == "File type":
                        item["Filename"] += "." + vals[i].text
                    elif not key in ["Size", "Document kind"]:
                        item["Info"][key] = vals[i].text
                    i += 1
                # items.add(item)
                    yield item

            if browser.find_element_by_xpath("//ul[@class='paging']/li[position()=last()]").text == "":
                break
#			break #debug
            # logging.log(logging.INFO,"[Progress] Page %s finished: Total %d items",page,len(items))

            try:
                browser.find_element_by_xpath(
                    "//ul[@class='paging']/li/span[@class='arrow']/a").click()
            except TimeoutException:
                pass
            t = AbbSpider.trytimes
        browser.quit()
        # return items
