## 进京证Python版
脚本说明：

- 删除了接口地址，避免造成无法承担的后果，有需要使用的请自行抓包

- 删除了接口部分参数，理由与上一条一致

- 脚本只包含两个功能：

  - getRemainingTime：获取剩余天数（同时获取了状态以及applyIdOld，后续会用到）

  - autoRenew：续签，当剩余天数小于一天时，调用续签方法

- 使用方法：
  - python3 jinjingzheng.py
-  其他玩法：
  - 脚本放到服务器上，执行一个计划任务，每7天执行一次，确保进京证永不过期（此方法适合6环外进京证办理，不限次数）
  - 没服务器的，放到自己笔记本上，也可以使用计划任务，同一（有树莓派的也可以）
  - 苹果手机可以下载Pythonista3（软件好像68元，自行购买或者找其他共享账号），可以直接在手机执行python脚本
- 再次声明：
  本脚本仅供爱好者使用，严禁以任何形式传播获利。本着方便快捷办理进京证的初衷，希望使用者也一起维护这份初衷。如有侵权，立删。
  针对脚本使用过程中，有任何问题可以随时联系本人，一起学习交流

- 新增功能：
  执行结果通过微信发送通知
  https://sct.ftqq.com/sendkey
  绑定自己的微信，生成SendKey，替换jinjingzheng.py 83行，就可以把执行结果通过微信发送到手机，方便及时查看。
  不喜欢的可以自行把main方法里的self.sendMsg(msg)删掉即可
