open-falcon 告警信息发送钉钉告警群
===
新入职公司目前使用的open-falcon监控，但是open-falcon监控支持短信，企业微信，邮件告警，对于现状，目前就只有邮件告警。其他前面两种都没有考虑。但邮件不是很及时。所以想将告警信息接入钉钉机器人。
## 配置
* 到open-falcon的alarm的/config/cgf.json配置post发送的端口。配置在im,sm上面都可以，使用一个没有用到的推送端口，该端口要与reboot_ding中的配置文件监听的端口一致。
* 修改该程序的config配置
* open-falcon中告警联系人的手机号如果填上了，那么rebot_ding会自动@此人

配置  |	说明
---|---
port  |	为open-falcon alarm配置上监听的端口
host  |	监听主机地址
tokenid |	钉钉机器人的tokenid
path |	日志存放的地址。默认为当前目录

* 在open-falcon 页面上，去吧要发送告警信息@的人的手机号写上。根据第一点，添在对应的位置。然后修改告警等级，改为3以下。

---
## 启动
```
python reboot_ding.py
```
> Note: 可以使用supervisor来进行托管启动