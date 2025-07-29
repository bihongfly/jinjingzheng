import sys
import requests
from datetime import datetime,timedelta

# 配置信息（需自行填写）
URL = "" # 初始地址，防止恶意访问，请求地址不提供，需要的自行抓包
AUTH = "" # 访问凭证，通过抓包在请求头信息 Authorization 字段
SEND_KEY = "" # server酱微信推送密钥(可选)

### 地理信息（按需改动，不懂可以不改。如需改动建议通过http://jingweidu.757dy.com/自行查询自己的经纬度）
SQDZGDJD = "116.269423" # 社区地址高德经度
SQDZGDWD = "40.211128" # 社区地址高德纬度
SQDZBDJD = "116.275203" # 社区地址百度经度
SQDZBDWD = "40.216228" # 社区地址百度纬度
XXDZ = "白浮泉公园" # 进京地址

# 接口地址（无需改动）
STATE_LIST_URL = f"https://{URL}/pro/applyRecordController/stateList" # 查询状态接口
INSERT_APPLY_RECORD_URL = f"https://{URL}/pro/applyRecordController/insertApplyRecord" # 办理续签接口

def request(url, payload={}) -> dict:
    headers = {"Authorization": AUTH, "Content-Type": "application/json"}
    res = requests.post(url, headers=headers, json=payload)
    data = res.json()
    if data["code"] == 200:
        return data
    else:
        print(f"请求失败，状态码: {data['code']}，错误信息: {data['msg']}")
        sys.exit(1)

def exec_renew(data, date, jjzzl="六环外") -> dict:
    payload = {
        "sqdzgdjd": SQDZGDJD,
        "sqdzgdwd": SQDZGDWD,
        "sqdzbdjd": SQDZBDJD,
        "sqdzbdwd": SQDZBDWD,
        "xxdz" : XXDZ,
        "hpzl" : data["hpzl"], # 车牌类型
        "applyIdOld" : data["applyId"], # 续办申请id
        "vId" : data["vId"], # 车辆识别代号
        "jsrxm" : data["jsrxm"], # 车主姓名
        "jszh" : data["jszh"], # 车主身份证号
        "hphm" : data["hphm"], # 车牌号
        "txrxx" : [],
        "jjdq" : "010", # 进京目的地地区
        "jjmd" : "06", # 进京目的地
        "jjzzl" : "01" if jjzzl == "六环内" else "02", # 进京证类型
        "jjlk" : "00606", # 进京路况
        "jjmdmc" : "其它", # 进京目的地名称
        "jjlkmc" : "其他道路", # 进京路况名称
        "jjrq" : date, # 进京日期(申请生效日期)
    }
    return request(INSERT_APPLY_RECORD_URL, payload)

def days_between_dates(date1: str, date2: str) -> int:
    d1 = datetime.strptime(date1, '%Y-%m-%d')
    d2 = datetime.strptime(date2, '%Y-%m-%d')
    return (d2 - d1).days + 1

def get_future_date(date_str, days) -> str:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    future_date = date_obj + timedelta(days=days)
    return future_date.strftime("%Y-%m-%d")

def send_wechat(title, msg) -> None:
    if not SEND_KEY:
        print("未配置server酱推送密钥，不发送微信推送")
        return
    requests.post(f"https://sctapi.ftqq.com/{SEND_KEY}.send?title={title}&desp={msg}")

def main():
    state_data = request(STATE_LIST_URL)
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

    yxqs, blztmc, jjzzlmc, sqsj, hphm = data['yxqs'], data['blztmc'], data["jjzzlmc"], data['sqsj'], data['hphm']
    yxqz = yxqz if data['yxqz'] else get_future_date(yxqs, 6)
    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = f"进京证{msg}: {yxqs[5:]}~{yxqz[5:]}"
    msg = f"{msg}\n状态: {blztmc}\n有效期: {yxqs}至{yxqz}\n类型: {jjzzlmc}\n申请时间: {sqsj}\n执行时间: {formatted_time}\n车牌号码: {hphm}"
    print(msg)
    send_wechat(title,msg)

if __name__ == "__main__":
    main()