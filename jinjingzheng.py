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
        auth = ""
        # 续签接口数据只展示部分说明，其他的需要自行抓包研究
        # 车主姓名
        user_name = ""
        # 车主身份证号
        id_num = ""
        # 车牌号
        plate_num = ""
        # 进京地址
        address = ""
        self.payload = {
            "sqdzgdjd" : "",
            "sqdzgdwd" : "",
            "sqdzbdjd" : "",
            "sqdzbdwd" : "",
            "jsrxm" : user_name,
            "jszh" : id_num,
            "hphm" : plate_num,
            "vId" : "",
            "applyIdOld" : "",
            "txrxx" : [
            ],
            "hpzl" : "",
            "jjdq" : "",
            "jjmd" : "",
            "jjzzl" : "",
            "jjlk" : "",
            "jjmdmc" : "其它",
            "jjlkmc" : "其他道路",
            "jjrq" : "", # 进京日期(申请生效日期)
            "xxdz" : address
        }
        self.headers = {
            "Authorization": auth,
            "Content-Type": "application/json"
        }

    def request(self, url, payload) -> dict:
        res = requests.post(url, headers=self.headers, data=payload)
        result = res.json()
        if result["code"] != 200:
            print(f"请求失败，状态码：{result['code']}，错误信息：{result['msg']}")
            sys.exit()
        return result

    # 获取申请状态
    def get_state_data(self) -> dict:
        result = self.request(self.state_url,payload = {})
        # 申请续签后，会有ecbzxx字段的数据显示审核通过(待生效)、以及最新的截止日期
        data = result["data"]["bzclxx"][0]["ecbzxx"][0] if result["data"]["bzclxx"][0]["ecbzxx"] else result["data"]["bzclxx"][0]["bzxx"][0]
        state_data = {
            "apply_id_old": data["applyId"],
            "current_state": data["blztmc"],
            "start_time": data["yxqs"],
            "end_time": data["yxqz"],
            "type": data["jjzzlmc"]
        }
        return state_data

    # 自动续签
    def auto_renew(self, payload) -> None:
        renew_result_json = self.request(self.inster_apply_record_url, payload)
        status_code = renew_result_json["code"]
        msg = renew_result_json["msg"]
        print(f"续签接口状态码：{status_code}")
        print(f"续签接口响应消息：{msg}")

    # 发送微信通知
    def send_wechat(self, send_key, title, msg):
        requests.post(f"https://sctapi.ftqq.com/{send_key}.send?title={title}&desp={msg}")

    def main(self):
        state_data = self.get_state_data()
        apply_id_old,current_state,end_time,type = state_data["apply_id_old"],state_data["current_state"],state_data["end_time"],state_data["type"]
        today = datetime.now().strftime("%Y-%m-%d")
        self.payload["applyIdOld"] = apply_id_old
        if current_state in ["审核通过(生效中)","审核中","审核通过(待生效)"]:
            # 如果当前状态是已经办理的情况，会有三种状态，则从明天开始续签
            msg= "无需续签"
            if current_state == "审核通过(生效中)":
                if end_time == today:
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    self.payload["jjrq"] = tomorrow
                    self.auto_renew(json.dumps(self.payload))
                    msg = "续签成功"
        else:
            # 如果不是以上三种状态，说明没有办理，则从今天开始续签
            self.payload["jjrq"] = today
            self.auto_renew(json.dumps(self.payload))
            msg = "续签成功"
        if msg == "续签成功":
            state_data = self.get_state_data()
        current_state,start_time,end_time = state_data["current_state"],state_data["start_time"],state_data["end_time"]
        title = f"{msg}：{start_time}至{end_time}"
        msg = f"{msg}：{start_time}至{end_time}，{current_state}-{type}"
        print(msg)
        send_key = ""
        self.send_wechat(send_key,title,msg)

AutoRenewTrafficPermit().main()