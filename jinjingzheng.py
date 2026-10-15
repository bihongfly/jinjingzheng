import sys
import requests
from datetime import datetime,timedelta

# 配置信息（需自行填写）
URL = "" # 初始地址，防止恶意访问，请求地址不提供，需要的自行抓包
AUTH = "" # 访问凭证，通过抓包在请求头信息 Authorization 字段
SEND_KEY = "" # IYUU微信推送密钥(可选)
JSRXM = "" # 驾驶人姓名（名下没有进京证时必须填写）
JSZH = "" # 驾驶人身份证号（名下没有进京证时必须填写）

# 地理信息（按需改动，不懂可以不改。如需改动建议通过http://jingweidu.757dy.com/自行查询自己的经纬度）
SQDZGDJD = "" # 社区地址高德经度
SQDZGDWD = "" # 社区地址高德纬度
SQDZBDJD = "" # 社区地址百度经度
SQDZBDWD = "" # 社区地址百度纬度
XXDZ = "" # 进京地址

# 接口地址（无需改动）
STATE_LIST_URL = f"https://{URL}/pro/applyRecordController/stateList" # 查询状态接口
INSERT_APPLY_RECORD_URL = f"https://{URL}/pro/applyRecordController/insertApplyRecord" # 办理续签接口

def request(url, payload={}):
    headers = {"Authorization": AUTH, "Content-Type": "application/json"}
    res = requests.post(url, headers=headers, json=payload, timeout=60)
    data = res.json()
    if data["code"] == 200:
        return data
    else:
        print(f"请求失败，状态码: {data['code']}，错误信息: {data['msg']}")
        send_wechat("进京证脚本出错", f"请求失败，状态码: {data['code']}，错误信息: {data['msg']}")
        sys.exit(1)

def exec_renew(data, date, jjzzl="六环外"):
    payload = {
        "sqdzgdjd": SQDZGDJD,
        "sqdzgdwd": SQDZGDWD,
        "sqdzbdjd": SQDZBDJD,
        "sqdzbdwd": SQDZBDWD,
        "xxdz" : XXDZ,
        "sfzj" : "1", # 是否在京
        "zjxxdz" : XXDZ, # 在京详细地址
        "hpzl" : data["hpzl"], # 车牌类型
        "vId" : data["vId"], # 车辆识别代号
        "jsrxm" : data.get("jsrxm") or JSRXM, # 车主姓名（没有证时用配置）
        "jszh" : data.get("jszh") or JSZH, # 车主身份证号（没有证时用配置）
        "hphm" : data["hphm"], # 车牌号
        "txrxx" : [],
        "jjdq" : "011", # 进京目的地地区
        "jjmd" : "06", # 进京目的地
        "jjzzl" : "01" if jjzzl == "六环内" else "02", # 进京证类型
        "jjlk" : "00606", # 进京路况
        "jjmdmc" : "其它", # 进京目的地名称
        "jjlkmc" : "其他道路", # 进京路况名称
        "jjrq" : date, # 进京日期(申请生效日期)
    }
    if data.get("applyId"):        # 只有续签才带；首次办理不发
        payload["applyIdOld"] = data["applyId"]
    return request(INSERT_APPLY_RECORD_URL, payload)

def send_wechat(title, msg):
    if SEND_KEY:
        requests.post(f"https://iyuu.cn/{SEND_KEY}.send?text={title}&desp={msg}")

def main():
    state_data = request(STATE_LIST_URL)
    cars = state_data["data"]["bzclxx"] or []
    if not cars:
        print("接口没有返回备案车辆，无法办理")
        send_wechat("错误", "没有返回备案车辆，无法办理")
        sys.exit(1)
    car = cars[0]
    recs = (car.get("ecbzxx") or []) or (car.get("bzxx") or [])
    data = recs[0] if recs else dict(car)
    yxqz, blztmc = data.get("yxqz"), data.get("blztmc")
    today = datetime.now().strftime("%Y-%m-%d")
    # flag=False 时原来没有 apply_date，展示区引用它会 NameError
    apply_date = None
    if blztmc in ["审核通过(生效中)", "审核中", "审核通过(待生效)", "已取消", "失败(审核不通过)"]:
        days_left = 99 # 审核中 / 失败(审核不通过) 时 yxqz 是 null，算不了天数
        if yxqz:
            days_left = (datetime.strptime(yxqz, '%Y-%m-%d') - datetime.strptime(today, '%Y-%m-%d')).days + 1
        if (blztmc == "审核通过(生效中)" and days_left <= 1) or blztmc in ["已取消", "失败(审核不通过)"]:
            apply_date, flag = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), True
        else:
            flag = False
    else:
        apply_date, flag = today, True
    if flag:
        exec_renew(data, apply_date)
        msg = "提交续签成功"
        state_data_new = request(STATE_LIST_URL)
        # data = state_data_new['data']['bzclxx'][0]['ecbzxx'][0]
        cars_new = state_data_new["data"]["bzclxx"] or []
        car_new = cars_new[0] if cars_new else car
        recs_new = (car_new.get("ecbzxx") or []) or (car_new.get("bzxx") or [])
        data = recs_new[0] if recs_new else data
        if not recs_new:
            blztmc = "已提交(待审核)"
    else:
        msg = "无需续签"
    yxqs = data.get("yxqs") or apply_date or today
    yxqz = data.get("yxqz") or (datetime.strptime(yxqs, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
    blztmc = data.get("blztmc") or blztmc or ""
    jjzzlmc = data.get("jjzzlmc") or "进京证(六环外)"
    sqsj = data.get("sqsj") or today
    hphm = data.get("hphm") or car.get("hphm") or ""
    exec_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = f"进京证{msg}: {yxqs[5:]}~{yxqz[5:]}"
    content = f"{msg}\n状态: {blztmc}\n有效期: {yxqs}至{yxqz}\n类型: {jjzzlmc}\n申请时间: {sqsj}\n执行时间: {exec_time}\n车牌号码: {hphm}"
    print(content)
    send_wechat(title, content)

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise # request() 里已经推过了，不重复推
    except Exception:
        import traceback
        detail = traceback.format_exc()
        print(detail)
        send_wechat("进京证脚本异常", detail[-400:])
        raise
