import random
import configparser
import os

import requests
import sys
from bs4 import BeautifulSoup

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")

# config
line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])

# weather_convert
city_chinese = ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣", "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義市", "嘉義縣", "宜蘭縣", "花蓮縣", "臺東縣", "臺南市", "高雄市", "屏東縣", "連江縣", "金門縣", "澎湖縣"]
city_english = ["Keelung", "Taipei", "New_Taipei", "Taoyuan", "Hsinchu", "Hsinchu", "Miaoli", "Taichung", "Changhua", "Nantou", "Yunlin", "Chiayi", "Chiayi", "Yilan", "Hualien", "Taitung", "Tainan", "Kaohsiung", "Pingtung", "Lienchiang", "Kinmen", "Penghu"]


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
    #for i in range(22):
    #if city == city_chinese[i] and city[2] == "市":
      #url = 'https://www.cwb.gov.tw/V7/forecast/taiwan/' + city_english[i] + '_City.htm'
      #break
    #elif city == city_chinese[i] and city[2] == "縣":
      #url = 'https://www.cwb.gov.tw/V7/forecast/taiwan/' + city_english[i] + '_County.htm'
      #break
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
      content = date_tags[5].get_text() + " " + temp_tag[0].get_text() + "℃" + " 降雨機率: " + temp_tag[3].get_text()
      # content = [date_tags[5].get_text() + " " + temp_tag[0].get_text() + "℃" + " 降雨機率: " + temp_tag[3].get_text()
                 # , date_tags[6].get_text() + " " + temp_tag[4].get_text() + "℃" + " 降雨機率: " + temp_tag[7].get_text()
                 # , date_tags[7].get_text() + " " + temp_tag[8].get_text() + "℃" + " 降雨機率: " + temp_tag[11].get_text()]
    return content
      #print(date_tags[5].get_text() + " " + temp_tag[0].get_text() + "℃" + " 降雨機率: " + temp_tag[3].get_text())
      #print(date_tags[6].get_text() + " " + temp_tag[4].get_text() + "℃" + " 降雨機率: " + temp_tag[7].get_text())
      #print(date_tags[7].get_text() + " " + temp_tag[8].get_text() + "℃" + " 降雨機率: " + temp_tag[11].get_text())

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
    # print("event.reply_token:", event.reply_token)
    # print("event.message.text:", event.message.text)
    # message = TextSendMessage(text=event.message.text)
    # line_bot_api.reply_message(event.reply_token, message)	

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    city = ""
    url = ""
    city = event.message.text.strip()
    if city[2] == "市":
        url = "City"
    elif city[2] == "縣":
        url = "County"
    if city in city_chinese:
        for i in range(22):
            if city == city_chinese[i]:
                target = i
                content = weather(city_english[target], url)
                #print(content)
                message = TextSendMessage(text=content)
                break
    else:
        message = TextSendMessage(text="請輸入正確縣市名稱")
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
