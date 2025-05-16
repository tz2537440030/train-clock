import requests

def push_to_wecom_robot():
    wx_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=10af027c-c51e-490d-a5be-7e9b89adb4aa'
    wx_headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": f"零食放包里！！！"
        }
    }
    requests.post(wx_url, json=data, headers=wx_headers)

push_to_wecom_robot()
