# ChatGPT完整实现定时请求小系统

Timed/interval initiation of HTTP requests.

![scheduledrequestschatgpt.png](https://cdn.wyr.me/post-files/2023-02-28/1677595282482/scheduled-requests-chatgpt.png)

**由ChatGPT实现，中文描述：**

使用python3实现一个定时请求服务，要求如下：

1、数据库使用sqlite3，代码中需要处理数据库初始化，数据库存储的内容可能存在中文。

2、python使用flask监听8848端口。

3、首页返回html内容，页面内容使用中文，使用bootstrap美化页面。页面中使用jquery的ajax实现用户登陆、退出、展示任务列表的功能，后端对应实现/api/login（登陆成功后使用jwt生成token返回前端，前端收到token后存储到localStorage）、/api/logout接口，同时编写三个需要token认证（token通过header传递）的POST接口实现/api/add、/api/remove，/api/list，分别用于添加任务、移除任务、展示任务列表。添加任务时需要输入任务URL、请求方式（GET/POST）、请求参数（如果是POST请求则可以选择body类型为json、x-www-form-urlencoded），同时可以选择定时方式——cron类型或固定时间间隔，如果用户选择cron类型则需要输入cron表达式，如果选择固定时间间隔，则需要输入数字秒。

4、进入页面的时候判断是否是否已经登陆（localStorage中是否存在token），如果存在则显示任务界面，否则显示登录界面。

5、前端与后端所有的交互需要使用json格式。

6、在python启动的时候，通过SQL查询所有的任务，加载任务到APScheduler，按照任务要求的间隔或cron时间定时执行对应方法及以对应参数请求对应的URL。

7、在任务执行失败的情况下进行错误处理。

8、默认账户密码为：admin、admin。

请实现完整的python代码。

**博文：** <https://www.wyr.me/post/733>

**视频：** <https://www.bilibili.com/video/BV1u84y1E79f/?share_source=copy_web&vd_source=de30ad927aff7c4075790b558eb50e56>

**提示：** 本文目的在于体现当时GPT3的能力，如有定时请求任务需求请使用成熟的任务调度系统。
