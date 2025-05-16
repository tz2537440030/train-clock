import requests
from datetime import datetime
import os
import sys
import logging
import time
from datetime import datetime

# 设置两个目标时间
morning_hour = 6
morning_minute = 50
morning_second = 0

evening_hour = 18
evening_minute = 0
evening_second = 0

def wait_until_target_time():
    while True:
        now = datetime.now()
        # 检查是否到达早上或晚上的目标时间
        if ((now.hour == morning_hour and now.minute == morning_minute and now.second == morning_second) or
            (now.hour == evening_hour and now.minute == evening_minute and now.second == evening_second)):
            break
        time.sleep(0.5)  # 休眠半秒，减少CPU占用

# 设置日志
log_file = "/Users/zhengtan/12306_train_info.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

url = "https://hzfw.12306.cn/zgzfw/trainTime/query"
# 请求参数
params1 = {
    "train_code": "G7201",
    "station_name": "昆山南",
    "from_to": "1"
}

params2 = {
    "train_code": "G7260",
    "station_name": "上海西",
    "from_to": "1"
}

# 请求头
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en,zh;q=0.9,zh-CN;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://hzfw.12306.cn/zgzfw/resources/web/zwdcx.html",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

def get_train_info(params):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # 检查响应状态
        data = response.json()
        if not data or 'data' not in data:
            print(f"警告：未获取到数据，响应内容：{data}")
            return None
        return data['data']
    except requests.exceptions.RequestException as e:
        print(f"请求错误：{e}")
        return None
    except ValueError as e:
        print(f"JSON解析错误：{e}")
        return None

def write_to_icloud_file(content, is_morning):    
    base_path = "/Users/zhengtan/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents"
    test_file = os.path.join(base_path, "test.txt")
    not_delay_file = os.path.join(base_path, "test-not-delay.txt")
    
    logging.info(f"开始处理文件操作，content: {content}")
    
    try:
        # 清空文件夹中的这两个文件
        for file_path in [test_file, not_delay_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"已删除文件：{os.path.basename(file_path)}")
        # 如果当前时间超过12点，就不执行
        # 如果content有值，创建test.txt
        if content and is_morning:
            with open(test_file, 'w') as f:
                f.write(content)
            logging.info("已创建文件：test.txt")
        else:
            logging.info("content为空，不创建任何文件")
            
    except Exception as e:
        logging.error(f"操作失败：{e}")

def format_train_message(message, is_morning):
    if not message:
        return "暂无列车信息"
        
    expected_times = {
        "G7201": "08:06",
        "G7260": "18:41"
    }
    lines = message.strip().splitlines()
    result_lines = []

    for line in lines:
        if "预计" in line and "出发时间为" in line:
            # 提取车次
            train_code = line.split("预计")[1].split("次")[0] + "次列车"
            station = line.split("，")[1].split("出发时间")[0]
            time = line.split("出发时间为")[1]

            code = train_code.replace("次列车", "")
            is_delayed = (code in expected_times and time != expected_times[code])

            if is_delayed:
                result_lines.append(f"【晚点】{time}")
                write_to_icloud_file("delayed", is_morning)
            else:
                result_lines.append(f"{time}")
                write_to_icloud_file("", is_morning)

        elif "暂无" in line:
            result_lines.append(line)
            write_to_icloud_file("", is_morning)

    return "\n".join(result_lines) if result_lines else "暂无列车信息"

def push_to_wecom_robot(message, is_morning):
    if not message:
        print("没有消息需要推送")
        return
        
    wx_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=10af027c-c51e-490d-a5be-7e9b89adb4aa'
    wx_headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": f"{format_train_message(message, is_morning)}"
        }
    }
    try:
        response = requests.post(wx_url, json=data, headers=wx_headers)
        response.raise_for_status()
        print("消息推送成功")
    except requests.exceptions.RequestException as e:
        print(f"推送消息失败：{e}")

# 程序执行后，每天6点50和18点自动查询G7201和G7260次列车正晚点信息，如果G7201次列车晚点，会在icloud新建一个文件，如果没有晚点会将文件删除，icloud会自动同步该文件夹，ios端会在6点51执行快捷指令，判断有没有该文件，存在的话，自动打开6点52的闹钟，否则关闭6点52的闹钟
def main():
    while True:
        logging.info("等待执行时间...")
        wait_until_target_time()
        
        logging.info("开始执行查询...")
        now = datetime.now()
        if now.hour < 12:
            train_info = get_train_info(params1)
            push_to_wecom_robot(train_info, True)
        else:
            train_info = get_train_info(params2)
            push_to_wecom_robot(train_info, False)
        
        logging.info("本次执行完成，等待下一次执行...")
        time.sleep(1)  # 等待1秒，避免重复执行

if __name__ == "__main__":
    main()
