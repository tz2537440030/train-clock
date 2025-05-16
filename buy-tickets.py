import requests
from datetime import datetime

today = datetime.now()
def push_to_wecom_robot(message):
    wx_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=10af027c-c51e-490d-a5be-7e9b89adb4aa'
    wx_headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": f"{message}"
        }
    }
    requests.post(wx_url, json=data, headers=wx_headers)

push_to_wecom_robot('【昆山】买票了！！！@谈证')
if today.month == 4 and today.day == 16:
    push_to_wecom_robot('【安庆】买票！！！@苏安妮')