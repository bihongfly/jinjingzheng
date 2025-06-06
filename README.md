## 进京证Python版
**脚本说明：(删除了部分参数以及接口地址，避免无谓的纷争，请自行抓包)**
### 功能介绍

本脚本的主要功能自动获取进京证状态，并自动办理。办理逻辑分为两种：
  - 1、进京证状态“未办理”，则自动办理当天的。
  - 2、进京证状态“已办理”，则到期前一天自动续签。

### 使用方法
  #### 1、微信通知：(可选)
  执行结果通过微信发送到手机，需要配置微信推送服务。我们通过server酱免费发送信息，每天可发5条。
  访问：[server酱](https://sct.ftqq.com/sendkey)， 使用自己微信登录，并获取SendKey
  [![pkM8sP0.png](https://s21.ax1x.com/2024/05/21/pkM8sP0.png)](https://imgse.com/i/pkM8sP0)
  复制上图中的SendKey，替换脚本中SEND_KEY = ""的值即可。

  #### 2、执行脚本：
  ```python3 jinjingzheng.py```

### 其他玩法：
  - 1、找一台可以长期运行的机器(服务器、主机、树莓派)，设计计划任务，每天执行脚本，确保进京证永不过期（此方法适合6环外进京证办理，不限次数）
  - 2、苹果手机可以下载Pythonista3(软件好像68元，自行购买或者找其他共享账号)，可以直接在手机执行python脚本。结合苹果自带的自动化，例如设置充满电的时候、某个时间点自动执行任务。
  - 3、(推荐)部署 [青龙](https://github.com/whyour/qinglong)，开源的定时任务管理平台，支持 Python3、JavaScript、Shell、Typescript

上面的脚本仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断。
仓库内所有资源文件，禁止任何公众号、自媒体进行任何形式的转载、发布。

本人对任何脚本问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害。
如果任何单位或个人认为该项目的脚本可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，我们将在收到认证文件后删除相关脚本。
您必须在下载后的24小时内从计算机或手机中完全删除以上内容.严禁产生利益链

创作不易，如果打赏咖啡者，请扫描下面二维码，感谢。(后续会推出Scriptable、快捷指令)
![pay](assets/pay.png "微信")

