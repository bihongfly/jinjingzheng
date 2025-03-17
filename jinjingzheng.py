import sys
import json
import requests
from datetime import datetime,timedelta

## 变量设置

### 接口信息
URL = "" # 初始地址，防止恶意访问，请求地址不提供，需要的自行抓包
AUTH = "" # 访问凭证，通过抓包在请求头信息 Authorization 字段
STATE_LIST_URL = f"https://{URL}/pro/applyRecordController/stateList" # 查询状态接口
INSERT_APPLY_RECORD_URL = f"https://{URL}/pro/applyRecordController/insertApplyRecord" # 办理续签接口

### 地理位置，经纬度信息(提示：如果不知道咋改，那就不要改！！想手动或自动生成请自行研究高德百度API)。
sqdzgdjd = "116.342573" # 进京经度
sqdzgdwd = "39.947399" # 进京纬度
sqdzbdjd = "116.342573" # 进京目的地经度
sqdzbdwd = "39.947399" # 进京目的地纬度
xxdz = "西直门外大街137号北京动物园" # 进京地址

### server酱微信推送密钥(可选)
SEND_KEY = ""

def request(url, payload) -> dict:
    headers = {
        "Authorization": AUTH,
        "Content-Type": "application/json"
    }
    res = requests.post(url, headers=headers, data=payload)
    data = res.json()
    if data["code"] == 200:
        return data
    else:
        print(f"请求失败，状态码: {data['code']}，错误信息: {data['msg']}")
        sys.exit(1)

def exec_renew(state_data, date, jjzzl="六环外") -> dict:
    jjzzl = "01" if jjzzl == "六环内" else "02" # 进京证类型
    jjdq = "010" # 进京目的地地区
    jjmd = "06" # 进京目的地
    jjlk = "00606" # 进京路况
    jjmdmc = "其它" # 进京目的地名称
    jjlkmc = "其他道路" # 进京路况名称
    jjrq = date # 进京日期(申请生效日期)

    # 接口自动返回个人信息，无需修改
    hpzl = state_data["hpzl"] # 车牌类型
    apply_id_old = state_data["applyId"] # 续办申请id
    vId = state_data["vId"] # # 车辆识别代号
    jsrxm = state_data["jsrxm"] # 车主姓名
    jszh = state_data["jszh"] # 车主身份证号
    hphm = state_data["hphm"] # 车牌号

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
        "jjmdmc" : jjmdmc,
        "jjlkmc" : jjlkmc,
        "applyIdOld" : apply_id_old,
        "jjrq" : jjrq,
        "vId" : vId,
        "jsrxm" : jsrxm,
        "jszh" : jszh,
        "hphm" : hphm,
        "xxdz" : xxdz
    }
    return request(INSERT_APPLY_RECORD_URL, json.dumps(payload))

def days_between_dates(date1_str, date2_str) -> int:
    try:
        date1 = datetime.strptime(date1_str, '%Y-%m-%d')
        date2 = datetime.strptime(date2_str, '%Y-%m-%d')
        time_difference = date2 - date1
        days_difference = time_difference.days + 1
        return days_difference
    except Exception as error:
        print("计算两个日期差失败:", error)
        return 0

def get_future_date(date_str, days) -> str:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    future_date = date_obj + timedelta(days=days)
    return future_date.strftime("%Y-%m-%d")

def send_wechat(title, msg) -> None:
    if SEND_KEY:
        requests.post(f"https://sctapi.ftqq.com/{SEND_KEY}.send?title={title}&desp={msg}")
    else:
        print("未配置server酱推送密钥，不发送微信推送")

def main():
    state_data = request(STATE_LIST_URL, payload = {})
    data = state_data["data"]["bzclxx"][0]["ecbzxx"][0] if state_data["data"]["bzclxx"][0]["ecbzxx"] else state_data["data"]["bzclxx"][0]["bzxx"][0]
    yxqz, blztmc = data["yxqz"], data["blztmc"]
    today = datetime.now().strftime("%Y-%m-%d")
    if blztmc in ["审核通过(生效中)", "审核中", "审核通过(待生效)", "已取消"]:
        days_difference = days_between_dates(today, yxqz)
        if (blztmc == "审核通过(生效中)" and days_difference <= 1) or blztmc == "已取消":
            apply_date, flag = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), True
        else:
            flag = False
    else:
        apply_date, flag = today, True

    if flag:
        renw_data = exec_renew(data, apply_date, jjzzl="六环外")
        msg = "续签成功" if renw_data["code"] == 200 else "续签失败"
        state_data_new = request(STATE_LIST_URL, payload = {})
        data = state_data_new['data']['bzclxx'][0]['ecbzxx'][0]
    else:
        msg = "无需续签"

    yxqs, blztmc, jjzzlmc, sqsj = data['yxqs'], data['blztmc'], data["jjzzlmc"], data['sqsj']
    yxqz = yxqz if data['yxqz'] else get_future_date(yxqs, 6)
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = f"进京证{msg}: {yxqs[5:]}~{yxqz[5:]}"
    msg = f"{msg}\n状态: {blztmc}\n有效期: {yxqs}至{yxqz}\n类型: {jjzzlmc}\n申请时间: {sqsj}\n执行时间: {formatted_time}"
    print(msg)
    send_wechat(title,msg)

if __name__ == "__main__":
    main()