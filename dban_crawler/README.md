### 模拟登陆某商城并爬取购物车数据

> Scrapy Version 1.6.0

- 使用验证码的登陆方式，打开APP端进行扫码即可。
- 默认使用MongoDB本地服务存储数据

## 如何获得呢?
关键数据
- callback=
- appid=
- token=

## 一
1. 获取二维码图片,通过

    `https://example.com/show?appid=133&size=147&t=`

    js 文件中，通过
    `var c = "//example.com/show?appid=" + (a || 133) + "&size=" + (b || 147) + "&t=" + (new Date).getTime();`可以获得参数值。

    同时，得到响应体中，发现`Set-Cookie: wlfstk_smdl=xxx`，调试js过程中发现，此即`token`的值。

2. 经观察发现此商城在登陆页面停留时，会不断地检测是否扫描二    维码，请求URL如下

    `https://example.com/check?callback=jQuery2963652&appid=133&token=iagj7vajd8k8in3xshpwmv9lh78900xi&_=1553070990901`

   `check`每隔一段时间检查是否扫描，基于此，程序也循环`check`，并以扫描后的特征值作为判断条件。

   callback 即 `callback=jQuery`加上一串数字，在js中如下
    ```js
    f.ajaxSetup({
        "jsonp": "callback",
        "jsonpCallback": function() {
            return "jQuery" + Math.floor(1e7 * Math.random())
        }
    ```

## 二
此时当我们扫描二维码并再一次进行上述的 `check` 时，可以看到响应发生了变化。并获得了一张 `ticket` 。

通过添加 `https://passport.jd.com/uc/qrCodeTicketValidation?t=` 中的 `t`，即 `ticket` ，得到 `{"returnCode":0, "url"="https://example.com"}` 的 JSON 数据证明登陆成功。获得的Cookie值则为最关键，作为后续登陆的 cookies。

> 附一张关于Scrapy简单的执行流的图片。