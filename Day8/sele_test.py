import requests
from selenium import webdriver
from bs4 import BeautifulSoup


driver = webdriver.Chrome('/Users/choikangseok/Desktop/KT_AI_P/Day8/chromedriver')
driver.get("https://www.google.com/search?q=%EA%B3%A0%EC%96%91%EC%9D%B4&rlz=1C5CHFA_enKR898&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjvi8vk2_3oAhVD63MBHbj_DQkQ_AUoAXoECBcQAw&biw=1280&bih=721")
driver.find_element_by_xpath('//*[@id="REsRA"]').clear()
driver.find_element_by_xpath('//*[@id="REsRA"]').send_keys("장범준")
driver.find_element_by_xpath('//*[@id="BIqFsb"]').click()
# search_box = driver.find_element_by_name("q")

# search_box.submit()
