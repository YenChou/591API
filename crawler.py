import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
all_list = []
head ={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
count = 1

from selenium.webdriver import Chrome
import time
driver = Chrome("./chromedriver")

for row in range(0,11340,30):
    print(row)
    driver.get('https://rent.591.com.tw/?kind=0&region=1&firstRow='+str(row))
    time.sleep(2)
    if row == 0:
         driver.find_element_by_xpath("/html/body/div[5]/div[1]/div[2]/dl[1]/dd[2]").click()
         time.sleep(2)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    h = soup.find("div",id="content").find_all('li',class_='infoContent')
    try:
        for i in h:
            http = "https:" + i.find('a').get('href').replace(" ",'')
            print(http)
            res = requests.get(http)
            html = BeautifulSoup(res.text)
            #內部開始
            info_dic = {}
            #title
            #房屋名稱
            name = html.find('span',class_='houseInfoTitle').text
            print(name)
            info_dic['房屋名稱'] = name
            #出租者身分
            rent_cat = html.find('div',class_ = 'avatarRight').text
            if rent_cat.find('服務費') != -1:
                rent_person_info = rent_cat.split('(')
                rent_person = rent_person_info[0].replace('\n','')
                info_dic['屋主名稱'] = rent_person
                rent_iden = rent_person_info[1].replace(")","")
                rent_iden = "仲介"

            elif rent_cat.find('屋主') != -1 :
                rent_person_info = rent_cat.split('（')
                rent_person = rent_person_info[0].replace('\n','')
                info_dic['屋主名稱'] = rent_person
                rent_iden = rent_person_info[1].replace("）","")
                rent_iden = "屋主"
            elif rent_cat.find('代理人'):
                rent_person_info = rent_cat.split('（')
                rent_person = rent_person_info[0].replace('\n','')
                info_dic['屋主名稱'] = rent_person
                rent_iden = rent_person_info[1].replace("）","")
                rent_iden = "代理人"
            info_dic['屋主身分'] = rent_iden
            print(rent_person)
            print(rent_iden)
            #電話
            tel = html.find('span',class_ = 'dialPhoneNum').get('data-value')
            info_dic['電話'] = tel
            print(tel)
            #價錢
            price_match = html.find('div',class_ = 'price clearfix').text.replace(',','')
            match = re.findall(r'\d+', price_match)
            price = match[0]
            info_dic['價錢'] = price
            print(price)
            #型態
            h_type = html.find("ul",class_ = 'attr')
            h_type2 = h_type.find_all('li')
            for h in h_type2:
                if h.text.find("型態") != -1:
                    info_dic['型態'] = h.text.replace("\xa0",'').split(":")[1]
                elif h.text.find("坪數") != -1:
                    info_dic["坪數"]  = h.text.replace("\xa0",'').split(":")[1]
                elif h.text.find("樓層") != -1:
                    info_dic["所在樓層"]  = h.text.replace("\xa0",'').split(":")[1].split("/")[0].replace('F','')
                    info_dic["總樓層"]  = h.text.replace("\xa0",'').split(":")[1].split("/")[1].replace('F','')
                elif h.text.find("現況") != -1:
                    info_dic["現況"]  = h.text.replace("\xa0",'').split(":")[1]
            #詳細資訊
            h_info = html.find("ul",class_ = "clearfix labelList labelList-1")
            h_info2 = h_info.find_all('li',class_ = "clearfix")
            for i in h_info2:
                title = i.find('div',class_='one')
                value = i.find('div',class_='two').text.replace("：",'')
                if title.text.find("押金") != -1:
                    info_dic['押金'] = value
                elif title.text.find("車 位") != -1:
                    info_dic['車位'] = value
                elif title.text.find("最短租期") != -1:
                    info_dic['最短租期'] = value
                elif title.text.find("性別要求") != -1:
                    info_dic['性別要求'] = value 
                elif title.text.find("可遷入日") != -1:
                    info_dic['可遷入日'] = value
                elif title.text.find("身份要求") != -1:
                    info_dic['身份要求'] = value
            #地址
            addr = html.find('span',class_ = "addr").text
            info_dic['地址'] = addr
            #地區
            head_r = html.find('div',id = 'propNav')
            head_l = head_r.find_all('a')
            region = head_l[3].text

            info_dic['地區'] = region
            #有效期
            dat = html.find('span',class_='ft-rt').text.split("：")[1]
            info_dic['有效期'] = dat

            print(info_dic)
            print(count)
            count +=1
            print('=================================================================')
            all_list.append(info_dic)
    except AttributeError:
        continue
pd.DataFrame(all_list).to_csv('./台北.csv',index=False,encoding='utf_8_sig')