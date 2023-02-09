import sys
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

    def log_info(self, msg):
        print(f"\033[01;34m{msg}\033[0m")

    def log_err(self, msg):
        print(f"\033[01;31m{msg}\033[0m")

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
        self.log_info(f"查询剩余天数状态码：{status_code}")
        self.log_info(f"查询剩余天数返回信息：{msg}")
        if status_code != 200:
            self.log_err("返回状态码不等于200，接口异常")
            sys.exit()
        current_state = state_result_json["data"]["bzclxx"][0]["bzxx"][0]["blztmc"]
        remaining_time = state_result_json["data"]["bzclxx"][0]["bzxx"][0]["sxsyts"]
        return current_state,remaining_time

    def autoRenew(self):
        current_state,remaining_time = self.getRemainingTime()
        self.log_info(f"进京证当前状态：{current_state}")
        self.log_info(f"剩余天数：{remaining_time}")
        if current_state == "审核通过(生效中)":
            self.log_info("生效中，无需重新申请")
            if remaining_time > 1:
                sys.exit()
            self.log_info("剩余时间小于1天，执行续签")
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            # 防止恶意访问，请求接口参数不做解释，需要的自行抓包
            payload = {
                "sqdzgdjd" : "",
                "txrxx" : [
                ],
                "hpzl" : "",
                "applyIdOld" : "",
                "sqdzgdwd" : "",
                "jjmdmc" : "",
                "jsrxm" : "",
                "jszh" : "",
                "jjdq" : "",
                "jjmd" : "",
                "sqdzbdjd" : "",
                "sqdzbdwd" : "",
                "jjzzl" : "",
                "jjlk" : "",
                "hphm" : "",
                "vId" : "",
                "jjrq" : tomorrow,
                "jjlkmc" : "",
                "xxdz" : ""
            }
            renew_result_json = self.request(self.inster_apply_record_url, payload)
            status_code = renew_result_json["code"]
            msg = renew_result_json["msg"]
            self.log_info(f"续签接口状态码：{status_code}")
            self.log_info(f"续签接口响应消息：{msg}")
            state_result_json = self.request(self.state_url,payload = {})
            current_state = state_result_json["data"]["bzclxx"][0]["ecbzxx"][0]["blztmc"]
            remaining_time = state_result_json["data"]["bzclxx"][0]["ecbzxx"][0]["sxsyts"]
            validity_period = state_result_json["data"]["bzclxx"][0]["ecbzxx"][0]["yxqs"] + "~" + state_result_json["data"]["bzclxx"][0]["ecbzxx"][0]["yxqz"]
            self.log_info(f"申请状态：{current_state}")
            self.log_info(f"生效时间：{validity_period}")

AutoRenewTrafficPermit().autoRenew()



