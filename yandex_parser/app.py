#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
py-parser_updated API
"""
from utils import *
import pickle
import re

import requests

from flask_restful import Api, Resource
from flask import request, Flask, jsonify, make_response
import time
from urllib.request import urlretrieve

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import os
from twocaptcha import TwoCaptcha
import pymongo

api_key = os.getenv('APIKEY_2CAPTCHA', 'api')

solver = TwoCaptcha(api_key)


app = Flask(__name__)
api = Api(app)

TAGS = ["span", "p"]


browser = prepare_driver()


def check_exists_by_xpath(xpath):
    try:
        browser.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def pass_captcha():
    captcha = browser.find_element(By.XPATH, '//*[@id="root"]/div/div/form')
    browser.get(captcha.get_attribute("action"))
    img = browser.find_element(By.XPATH, '//*[@id="advanced-captcha-form"]/div/div[1]/img')
    src = img.get_attribute('src')
    urlretrieve(src, "image.png")
    solved = solver.normal(r'./image.png')
    if solved.get("code"):
        print(solved['code'])
        input_fld = browser.find_element(By.XPATH, '//*[@id="xuniq-0-1"]')
        input_fld.send_keys(solved['code'])
        input_fld.send_keys(Keys.ENTER)


def get_subs(damn):
    sx = damn.find_elements(By.CSS_SELECTOR, "div._3VMnE ul li a")
    return [{"catalogue_name": jj.text, "catalogue_url": jj.get_attribute("href")} for jj in sx if "list" in jj.get_attribute("href")]


def click_events():
    try:
        clickable = browser.find_elements(By.CSS_SELECTOR, "span._2Pukk")
        for i in clickable:
            i.click()
    except NoSuchElementException:
        pass


def parse_items():
    tovary = []
    if check_exists_by_xpath('//*[@id="root"]/div/div/form'):
        pass_captcha()
    try:
        browser.find_element(By.XPATH, "/html/body/div[15]/div/div[2]/div/div[1]")
    except:
        pass
    try:
        browser.find_element(By.XPATH, '//*[@id="serpTop"]/div/div/div[3]/div/div/div/label[1]/input').click()
        time.sleep(2)
        try:
            browser.find_element(By.CSS_SELECTOR, "button._2AMPZ._1N_0H._1ghok._390_8").click()
            time.sleep(2)
        except:
            pass
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)
        all_items = browser.find_elements(By.CSS_SELECTOR, "article._2vCnw.cia-vs.cia-cs")
        for item2 in all_items:
            try:
                a_tag = item2.find_element(By.CSS_SELECTOR, "a._2f75n._24Q6d.cia-cs")
                title = a_tag.get_attribute("title")
                linka = a_tag.get_attribute("href")
                img = item2.find_element(By.CSS_SELECTOR, "img._2UO7K").get_attribute("src")
                price = item2.find_element(By.CSS_SELECTOR, "div._3NaXx._33ZFz._2m5MZ").find_element(By.CSS_SELECTOR, "span").text
                specification = item2.find_elements(By.CSS_SELECTOR, "ul.fUyko._2LiqB li")
                all_specs = []
                for specific in specification:
                    initial_val = specific.text
                    print(initial_val)
                    if ":" in initial_val:
                        val_type = initial_val.split(":")[0]
                        val_val = initial_val.split(":")[1].strip()
                    else:
                        val_type, val_val = "", ""
                    all_specs.append({"initial": initial_val, "parsed_type": val_type, "parse_value": val_val})
                print(all_specs, flush=True)
                tovary.append({"title": title, "url": linka, "img": img, "price": price, "specs": all_specs})
            except:
                pass
    except NoSuchElementException as e:
        print(e)
    return tovary


def get_specs():
    array = []
    try:
        click_events()
        all_data = browser.find_elements(By.CSS_SELECTOR, "div._1WWgS div[data-zone-data] fieldset._3n_-4")
        textes = []
        clean = []
        for ij in all_data:
            try:
                textss = ij.find_element(By.CSS_SELECTOR, "legend").text
            except:
                textss = None
            if textss not in textes:
                clean.append(ij)
            else:
                textes.append(ij.find_element(By.CSS_SELECTOR, "legend").text)
        for ii in clean:
            try:
                field_name = ii.find_element(By.CSS_SELECTOR, "legend").text
            except NoSuchElementException:
                field_name = ""
            d = {"Field_Name": field_name}
            if d["Field_Name"]:
                try:
                    vals = ii.find_elements(By.CSS_SELECTOR, "div.XkAMv._1hnnU")
                except NoSuchElementException:
                    vals = []
                if vals:
                    for jj in vals:
                        d["values"] = [i.text for i in jj.find_elements(By.CSS_SELECTOR, "div.XkAMv._1hnnU div._2XVtn")]
            if d.get("values"):
                array.append(d)
    except:
        pass
    return array


class Health(Resource):
    """Health checking"""

    def get(self):
        print('health checked')
        return make_response(jsonify({'status': 'OK'}), 200)

    def post(self):
        print('health checked')
        return make_response(jsonify({'status': 'OK'}), 200)


class Parse(Resource):

    def get(self):
        url = request.get_json().get("url")
        if not url:
            return {"status": "No link provided"}
        browser.get(url)
        cookies = pickle.load(open(r"./cookies/cookies.pkl", "rb"))
        for cookie in cookies:
            browser.add_cookie(cookie)
        if check_exists_by_xpath('//*[@id="root"]/div/div/form'):
            pass_captcha()
        try:
            clickable = browser.find_elements(By.CSS_SELECTOR, "div._2et7a.egKyN.n1VbV._2oLyz._9qbcy.gmQcK")
            for c in clickable:
                c.click()
        except NoSuchElementException:
            print("No еще", flush=True)
        all_subclasses = browser.find_elements(By.CSS_SELECTOR, "div._1YdrM")
        collection_fo_hierarchy = []
        print(len(all_subclasses))
        for iik in all_subclasses:
            hierarchy = {}
            d = iik.find_element(By.CSS_SELECTOR, "div a")
            print(d.text)
            hierarchy["catalogue_main"] = d.text
            hierarchy["catalogue_main_url"] = d.get_attribute("href")
            if "list" not in hierarchy["catalogue_main_url"]:
                hierarchy["sub_catalogues"] = get_subs(iik)
            else:
                hierarchy["sub_catalogues"] = []
            print(hierarchy)
            collection_fo_hierarchy.append(hierarchy)

        for colection in collection_fo_hierarchy:
            if colection["sub_catalogues"]:
                for hier in colection["sub_catalogues"]:
                    browser.get(hier["catalogue_url"])
                    if check_exists_by_xpath('//*[@id="root"]/div/div/form'):
                        pass_captcha()
                    hier["specs"] = get_specs()
                    hier["items"] = parse_items()
            elif "list" in colection["catalogue_main_url"]:
                browser.get(colection["catalogue_main_url"])
                if check_exists_by_xpath('//*[@id="root"]/div/div/form'):
                    pass_captcha()
                colection["specs"] = get_specs()
                colection["items"] = parse_items()
            else:
                colection["specs"] = []
        return collection_fo_hierarchy


api.add_resource(Health, '/api/', '/api/health')
api.add_resource(Parse, '/api/parse')

if __name__ == '__main__':
    app.run()
