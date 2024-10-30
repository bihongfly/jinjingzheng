import sys
import json
import requests
from datetime import datetime,timedelta

## 变量设置

### api地址
URL = "" # 初始地址，防止恶意访问，请求地址不提供，需要的自行抓包
STATE_LIST_URL = f"https://{URL}/pro/applyRecordController/stateList" # 查询状态接口
INSERT_APPLY_RECORD_URL = f"https://{URL}/pro/applyRecordController/insertApplyRecord" # 办理续签接口

### 车主基本信息
AUTH = "" # 访问凭证，通过抓包在请求头信息 Authorization 字段
USERNAME = "" # 车主姓名
ID_NO = "" # 车主身份证号
LICENSE_PLATE_NUMBER = "" # 车牌号
ADDR = "" # 进京地址
VID = "" # 车辆识别代号

### 经纬度地址等信息(可使用geo库自动生成)
sqdzgdjd = "" # 进京经度
sqdzgdwd = "" # 进京纬度
sqdzbdjd = "" # 进京目的地经度
sqdzbdwd = "" # 进京目的地纬度
hpzl = "" # 车牌类型
jjdq = "" # 进京目的地地区
jjmd = "" # 进京目的地
jjzzl = "" # 进京证类型
jjlk = "" # 进京路况

### server酱微信推送密钥(可选)
send_key = ""

def request(url, payload) -> dict:
    headers = {
        "Authorization": AUTH,
        "Content-Type": "application/json"
    }
    res = requests.post(url, headers=headers, data=payload)
    result = res.json()
    if result["code"] != 200:
        print(f"请求失败，状态码: {result['code']}，错误信息: {result['msg']}")
        sys.exit(1)
    return result

def get_state_data() -> dict:
    return request(STATE_LIST_URL, payload = {})

def exec_renew(apply_id_old,jjrq):
    payload = {
        "sqdzgdjd" : sqdzgdjd,
        "sqdzgdwd" : sqdzgdwd,
        "sqdzbdjd" : sqdzbdjd,
        "sqdzbdwd" : sqdzbdwd,
        "txrxx" : [],
        "hpzl" : hpzl,
        "jjdq" : jjdq,
        "jjmd" : jjmd,
        "jjzzl" : jjzzl,
        "jjlk" : jjlk,
        "jjmdmc" : "其它", # 进京目的地名称
        "jjlkmc" : "其他道路", # 进京路况名称
        "applyIdOld" : apply_id_old, # 续办申请id
        "jjrq" : jjrq, # 进京日期(申请生效日期)
        "vId" : VID,
        "jsrxm" : USERNAME,
        "jszh" : ID_NO,
        "hphm" : LICENSE_PLATE_NUMBER,
        "xxdz" : ADDR
    }
    return request(INSERT_APPLY_RECORD_URL, json.dumps(payload))

def days_between_dates(date1_str, date2_str):
    try:
        date1 = datetime.strptime(date1_str, '%Y-%m-%d')
        date2 = datetime.strptime(date2_str, '%Y-%m-%d')
        time_difference = date2 - date1
        days_difference = time_difference.days + 1
        return days_difference
    except Exception as error:
        print("计算两个日期差失败:", error)
        return 0

def get_future_date(date_str, days):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    future_date = date_obj + timedelta(days=days)
    return future_date.strftime("%Y-%m-%d")

def send_wechat(title, msg):
    requests.post(f"https://sctapi.ftqq.com/{send_key}.send?title={title}&desp={msg}")

def main():
    state_data = get_state_data()
    data = state_data["data"]["bzclxx"][0]["ecbzxx"][0] if state_data["data"]["bzclxx"][0]["ecbzxx"] else state_data["data"]["bzclxx"][0]["bzxx"][0]
    yxqz = data["yxqz"]
    blztmc = data["blztmc"]
    apply_id_old = data["applyId"]
    today = datetime.now().strftime("%Y-%m-%d")
    days_difference = days_between_dates(today, yxqz)
    msg = "无需续签"
    if blztmc in ["审核通过(生效中)", "审核中", "审核通过(待生效)"]:
        if blztmc == "审核通过(生效中)" and days_difference <= 1:
            jjrq, msg = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), "续签成功"
    else:
        jjrq, msg = today, "续签成功"

    if msg == "续签成功":
        renw_data = exec_renew(apply_id_old,jjrq)
        msg = "续签成功" if renw_data["code"] == 200 else "续签失败"
        state_data_new = get_state_data()
        data = state_data_new['data']['bzclxx'][0]['ecbzxx'][0]
    yxqs = data['yxqs']
    yxqz = yxqz if data['yxqz'] else get_future_date(yxqs, 6)
    blztmc = data['blztmc']
    jjzzlmc = data['jjzzlmc']
    sqsj = data['sqsj']
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = f"进京证{msg}: {yxqs[5:]}~{yxqz[5:]}"
    msg = f"{msg}\n状态: {blztmc}\n有效期: {yxqs}至{yxqz}\n类型: {jjzzlmc}\n申请时间: {sqsj}\n执行时间: {formatted_time}"
    print(msg)
    send_wechat(title,msg)

if __name__ == "__main__":
    main()