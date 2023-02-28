import sys
import json
import requests
from datetime import datetime,timedelta

class AutoRenewTrafficPermit(object):
    def __init__(self):
        # 初始地址，防止恶意访问，请求地址不提供，需要的自行抓包
        url = ""
        # 查询状态接口
        self.state_url = f"https://{url}/pro/applyRecordController/stateList"
        # 办理续签接口
        self.inster_apply_record_url = f"https://{url}/pro/applyRecordController/insertApplyRecord"
        # 访问凭证，通过抓包在请求头信息 Authorization 字段
        self.auth = ""
        # 续签接口数据只展示部分说明，其他的需要自行抓包研究
        # 车主姓名
        user_name = ""
        # 车主身份证号
        id_num = ""
        # 车牌号
        plate_num = ""
        # 进京地址
        address = ""
        # 以申请明天开始为例
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.payload = {
            "sqdzgdjd" : "",
            "txrxx" : [
            ],
            "hpzl" : "",
            "applyIdOld" : "",
            "sqdzgdwd" : "",
            "jjmdmc" : "其它",
            "jsrxm" : user_name,
            "jszh" : id_num,
            "jjdq" : "",
            "jjmd" : "",
            "sqdzbdjd" : "",
            "sqdzbdwd" : "",
            "jjzzl" : "",
            "jjlk" : "",
            "hphm" : plate_num,
            "vId" : "",
            "jjrq" : tomorrow,
            "jjlkmc" : "其他道路",
            "xxdz" : address
        }

    def request(self, url, payload):
        headers = {
            "Authorization": self.auth
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        res_result_json = response.json()
        return res_result_json

    def getRemainingTime(self):
        payload = {}
        state_result_json = self.request(self.state_url, payload)
        status_code = state_result_json["code"]
        msg = state_result_json["msg"]
        print(f"查询剩余天数状态码：{status_code}")
        print(f"查询剩余天数返回信息：{msg}")
        if status_code != 200:
            print("返回状态码不等于200，接口异常")
            sys.exit()
        current_state = state_result_json["data"]["bzclxx"][0]["bzxx"][0]["blztmc"]
        remaining_time = state_result_json["data"]["bzclxx"][0]["bzxx"][0]["sxsyts"]
        apply_id_old = state_result_json["data"]["bzclxx"][0]["bzxx"][0]["applyId"]
        print(f"进京证当前状态：{current_state}")
        print(f"剩余天数：{remaining_time}")
        return current_state,remaining_time,apply_id_old

    def autoRenew(self, payload):
        renew_result_json = self.request(self.inster_apply_record_url, payload)
        status_code = renew_result_json["code"]
        msg = renew_result_json["msg"]
        print(f"续签接口状态码：{status_code}")
        print(f"续签接口响应消息：{msg}")
        state_result_json = self.request(self.state_url,payload = {})
        if state_result_json["data"]["bzclxx"][0]["ecbzxx"]:
            current_state = state_result_json["data"]["bzclxx"][0]["ecbzxx"][0]["blztmc"]
            validity_period = state_result_json["data"]["bzclxx"][0]["ecbzxx"][0]["yxqs"] + "~" + state_result_json["data"]["bzclxx"][0]["ecbzxx"][0]["yxqz"]
            print(f"申请状态：{current_state}")
            print(f"生效时间：{validity_period}")

    def main(self):
        current_state,remaining_time,apply_id_old = self.getRemainingTime()
        self.payload["applyIdOld"] = apply_id_old
        payload = json.dumps(self.payload)
        if current_state == "审核通过(生效中)":
            print("生效中，无需重新申请")
            if remaining_time > 1:
                sys.exit()
            print("剩余时间小于1天，执行续签")
            self.autoRenew(payload)
        else:
            self.autoRenew(payload)

AutoRenewTrafficPermit().main()