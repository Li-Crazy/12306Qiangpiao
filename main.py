'''
-*- coding: utf-8 -*-
@Author  : LiZhichao
@Time    : 2019/5/29 21:25
@Software: PyCharm
@File    : main.py
'''
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#
# driver_path = r'C:\geckodriver\geckodriver.exe'
# driver = webdriver.Firefox(executable_path=driver_path)

class Qiangpiao(object):
    def __init__(self):
        self.driver = webdriver.Firefox(executable_path="C:\geckodriver\geckodriver.exe")
        self.login_url = "https://kyfw.12306.cn/otn/login/init"
        self.initmy_url = "https://kyfw.12306.cn/otn/view/index.html"
        self.search_url = "https://kyfw.12306.cn/otn/leftTicket/init"
        self.passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDo"

    def wait_input(self):
        self.from_station = input("起始站：")
        self.to_station = input("目的地：")
        #时间格式应与网站一致yyyy-mm-dd
        self.depart_time = input("出发时间：")
        self.passengers = input("乘客姓名（如何有多个乘客，用英文逗号分隔）:").split(",")
        self.trains = input("车次（如何有多个车次，用英文逗号分隔）:").split(",")

    def _login(self):#加下划线，不想让外界调用该函数，但是外界可以调用
        self.driver.get(self.login_url)
        #显示等待，在一定时间范围等待，来了则不再等待
        WebDriverWait(self.driver,1000).until(EC.url_to_be(self.initmy_url))
        #隐示等待，在一定时间范围等待，不管来不来都等待一定时间
        print("登录成功")

    def _order_ticket(self):
        #1.跳转到查余票页面
        self.driver.get(self.search_url)
        #2.等待出发地是否正确
        WebDriverWait(self.driver,1000).until(
            EC.text_to_be_present_in_element_value((By.ID,"fromStationText"),self.from_station)
        )
        #3.等待目的地是否正确
        WebDriverWait(self.driver,1000).until(
            EC.text_to_be_present_in_element_value((By.ID,"toStationText"),
                                                   self.to_station)
        )
        #4.等待出发日期是否正确
        WebDriverWait(self.driver,1000).until(
            EC.text_to_be_present_in_element_value((By.ID,"train_date"),self.depart_time)
        )
        #5.等待查询按钮是否可用
        WebDriverWait(self.driver,1000).until(
            EC.element_to_be_clickable((By.ID,"query_ticket"))
        )
        #6.按钮可用，执行点击事件
        searchBtn = self.driver.find_element_by_id("query_ticket")
        searchBtn.click()
        #7.点击查询按钮后，等待车次信息是否显示出来
        WebDriverWait(self.driver,1000).until(
            EC.presence_of_element_located((By.XPATH,".//tbody["
                                                     "@id='queryLeftTable']/tr"))
        )
        #8.找到所有没有datatrain属性的tr标签，这些标签包含车次信息
        tr_list = self.driver.find_elements_by_xpath(".//tbody["
                                                     "@id='queryLeftTable']/tr[not(@datatrain)]")
        #9.遍历所有满足条件的tr标签
        for tr in tr_list:
            train_number = tr.find_element_by_class_name("number").text
            # print(train_number)
            # print('='*30)
            if train_number in self.trains:
                left_ticket = tr.find_element_by_xpath(".//td[4]").text
                if left_ticket == "有" or left_ticket.isdigit:
                    # print(train_number + "有票")
                    orderBtn = tr.find_element_by_class_name("btn72")
                    orderBtn.click()

                    #等待是否来到确认乘客页面
                    WebDriverWait(self.driver,1000).until(
                        EC.url_to_be(self.passenger_url)
                    )

                    # 等待所有乘客信息是否被加再进来
                    WebDriverWait(self.driver, 1000).until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, ".//ul[@id='normal_passenger_id']/li")
                        )
                    )

                    # 获取所有乘客信息
                    passenger_labels = self.driver.find_elements_by_xpath(
                        ".//ul[@id='normal_passenger_id']/li/label")
                    for passenger_label in passenger_labels:
                        name = passenger_label.text
                        if name in self.passengers:
                            passenger_label.click()

                    # 获取提交订单按钮，购票
                    submitBtn = self.driver.find_element_by_id("submitOrder_id")
                    submitBtn.click()

                    # 判断确认订单的对话框是否出现
                    WebDriverWait(self.driver, 1000).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "dhtmlx_wins_body_outer"))
                    )

                    # 判断确认按钮出现
                    WebDriverWait(self.driver, 1000).until(
                        EC.presence_of_element_located((By.ID, "qr_submit_id"))
                    )

                    # 点击确认按钮
                    confirmBtn = self.driver.find_element_by_id("qr_submit_id")
                    confirmBtn.click()
                    while confirmBtn:
                        confirmBtn.click()
                        confirmBtn = self.driver.find_element_by_id("qr_submit_id")

                    return


    def run(self):
        self.wait_input()
        self._login()
        self._order_ticket()

if __name__ == '__main__':
    spider = Qiangpiao()
    spider.run()
