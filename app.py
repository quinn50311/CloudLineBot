import random
import configparser
import os
import re
import json
from pyquery import PyQuery as pq

import datetime
import requests
import sys
import time
from bs4 import BeautifulSoup

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from linebot.models import TextSendMessage

headers = {
	'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Mobile Safari/537.36'
	,'cookie':'mid=W7JKBgALAAFle1fo1DmXlbZrevRd; mcd=3; csrftoken=FAaVU2r9OH2eXDqXtOA5G497TPH1McQm; ds_user_id=1516703459; sessionid=1516703459%3AIAH4lVUMx8vtij%3A27; fbm_124024574287414=base_domain=.instagram.com; rur=FRC; shbid=15998; shbts=1555521409.487367; urlgen="{\"220.137.119.99\": 3462}:1hGwIw:jYKWxz6LdCVqAUcnBGCQJY5NBeo"' 
}

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")

# config
line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])

# weather_convert
city_chinese = ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣", "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義市", "嘉義縣", "宜蘭縣", "花蓮縣", "臺東縣", "臺南市", "高雄市", "屏東縣", "連江縣", "金門縣", "澎湖縣"]
city_english = ["Keelung", "Taipei", "New_Taipei", "Taoyuan", "Hsinchu", "Hsinchu", "Miaoli", "Taichung", "Changhua", "Nantou", "Yunlin", "Chiayi", "Chiayi", "Yilan", "Hualien", "Taitung", "Tainan", "Kaohsiung", "Pingtung", "Lienchiang", "Kinmen", "Penghu"]
Weather = ["天氣", "氣象", "weather"]
Train = ["時刻表", "火車時刻表", "火車"]
ig = ["Instagram", "instagram", "IG", "ig", "Ig", "iG"]
User_id = "1"

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except:
        print("something wrong")
    return 'OK'


def weather(city, url):
    content = ""
    target_url = 'https://www.cwb.gov.tw/V7/forecast/taiwan/' + city + '_' + url + '.htm'
    

    #向中央氣象局發一個url的request
    r = requests.get(target_url)
    #把中文亂碼轉正常中文
    r.encoding = 'UTF-8'
    # 確認是否下載成功
    if r.status_code == requests.codes.ok:
      # 以 BeautifulSoup 解析 HTML 原始碼
      soup = BeautifulSoup(r.text, 'html.parser')

      #抓收到的所有跟th、td有關的html資料
      date_tags = soup.find_all("th")
      temp_tag = soup.find_all("td")
      content = (date_tags[5].get_text().split(' ', 1)[0] + "\n" 
                 + date_tags[5].get_text().split(' ', 1)[1] + "\n" 
                 + "溫度:" + temp_tag[0].get_text() + "℃" + "\n" 
                 + "降雨機率:" + temp_tag[3].get_text() + "\n\n" 
                 + date_tags[6].get_text().split(' ', 1)[0] + "\n"
                 + date_tags[6].get_text().split(' ', 1)[1] + "\n" 
                 + "溫度:" + temp_tag[4].get_text() + "℃" + "\n" 
                 + "降雨機率:" + temp_tag[7].get_text() + "\n\n" 
                 + date_tags[7].get_text().split(' ', 1)[0] + "\n" 
                 + date_tags[7].get_text().split(' ', 1)[1] + "\n" 
                 + "溫度:" + temp_tag[8].get_text() + "℃" + "\n" 
                 + "降雨機率: " + temp_tag[11].get_text())

    return content

def train_time(train_stop1, train_stop2):
    content = ""
    target_url = "https://tw.piliapp.com/%E5%8F%B0%E9%90%B5%E7%81%AB%E8%BB%8A%E6%99%82%E5%88%BB%E8%A1%A8/"
    my_params = {'q': train_stop1 + ' ' + train_stop2}
    r = requests.get(target_url, params = my_params)
    r.encoding = 'UTF-8'
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        time_tag = soup.find_all("td")
        time = datetime.datetime.now()
        time = int(time.hour) + 8
        time1 = time + 1
        time_start = 4
        name = ' ' + "  車種" + "    開車 " + " 到達"   
        content = content + name + '\n'
        for i in range(4, len(time_tag), 10):
            if str(time) == str(time_tag[time_start])[4:6] or str(time1) == str(time_tag[time_start])[4:6]:
                index = time_tag.index(time_tag[time_start])
                if (index - 4) % 10 == 0:
                    if str(time_tag[index - 4])[6] != "<":
                        all = str(time_tag[index - 4])[4:7] + " " + str(time_tag[index])[4:9] + " " + str(time_tag[index + 1])[4:9]
                    else:
                        all = str(time_tag[index - 4])[4:6] + "號" + " " + str(time_tag[index])[4:9] + " " + str(time_tag[index + 1])[4:9]
                    content = content + all + "\n"
                else:
                    time_tag[index] = int(str(time_tag[index])[4:6]) - 1
                    time_start = time_start - 10
            time_start = time_start + 10
    return content

def get_html(url):
	try:
		response = requests.get(url, headers=headers)
		if response.status_code == 200:
			return response.text
		else:
			print('請求錯誤狀態碼:', response.status_code)
	except Exception as e:
			print(e)
			return None


def get_urls(html):
	urls = []
	doc = pq(html)
	items = doc('script[type="text/javascript"]').items()
	for item in items:
		if item.text().strip().startswith('window._sharedData'):
			js_data = json.loads(item.text()[21:-1], encoding='utf-8')
			edges = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
			page_info = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]
			cursor = page_info['end_cursor']
			flag = page_info['has_next_page']
			for edge in edges:
				if edge['node']['display_url']:
					display_url = edge['node']['display_url']
					print(display_url)
					urls.append(display_url)
			#print(cursor, flag)
	return urls

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    #get user id
    User_id = event.source.user_id
    print(User_id)
    cmd = ""
    argv1 = ""
    argv2 = ""
    city = ""
    url = ""
    train_stop1 = ""
    train_stop2 = ""
    URL_base = "https://www.instagram.com/"
    URL = ""
    text = event.message.text.strip()
    cmd = text.split()[0].lower()

    if len(text.split()) == 2:
        argv1 = text.split()[1]
    elif len(text.split()) == 3:
        argv1 = text.split()[1]
        argv2 = text.split()[2]
		
    print(cmd + ' ' + argv1 + '  ' + argv2)
    if cmd in Weather:
        city = argv1.strip()
        if city[2] == "市" and city[0] == "台":
            city[0] = "臺"
            url = "City"
        elif city[2] == "縣" and city[0] == "台":
            city[0] = "臺"
            url = "County"
        elif city[2] == "市":
            url = "City"
        elif city[2] == "縣":
            url = "County"

        if city in city_chinese:
            for i in range(22):
                if city == city_chinese[i]:
                    target = i
                    content = weather(city_english[target], url)
                    message = TextSendMessage(text=content)
                    break
        else:
            message = TextSendMessage(text="請輸入正確縣市名稱")

    elif cmd in Train:
        train_stop1 = argv1.strip()
        train_stop2 = argv2.strip()
        content = train_time(train_stop1, train_stop2)
        message = TextSendMessage(text=content)
		
    elif cmd == "功能":
        content = "輸入(天氣 縣市)就可以看天氣唷~" + "\n" + "輸入(火車 起站 迄站)就可以查時刻表喔(不過需要直達車!!!)"
        message = TextSendMessage(text=content)

    elif cmd in ig:
        URL = URL_base + argv1.strip() + "/"
        html = get_html(URL)
        URLs = get_urls(html)
        message = TextSendMessage(text=URLs)

    line_bot_api.reply_message(event.reply_token, message)

@handler.add(MessageEvent, message=StickerMessage)  
def handle_sticker_message(event):
    print("package_id:", event.message.package_id)
    print("sticker_id:", event.message.sticker_id)
    sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                   126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    sticker_message = StickerSendMessage(package_id='1', sticker_id=sticker_id)
    line_bot_api.reply_message(event.reply_token, sticker_message)   

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
