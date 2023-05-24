const API = "URL地址自行抓包" + "/pro/applyRecordController/stateList"
let data = await getData(API)
let widget = await createWidget(data)

if (!config.runsInWidget) {
    await widget.presentMedium()
}
Script.setWidget(widget)
Script.complete()

async function createWidget(data) {
    let w = new ListWidget()
    w.setPadding(10, 10, 5, 10)
    bg = new LinearGradient()
    bg.locations = [0,1]
    bg.colors = [
        new Color("#9ab8eb", 1),
        new Color("#ebe8f3",1)
    ]
    w.backgroundGradient = bg

    const wrap = w.addStack()
    wrap.layoutHorizontally()
    wrap.spacing = 15
    const column0 = wrap.addStack()
    column0.layoutVertically()

    let TypeStack = column0.addStack()
    TypeStack.layoutVertically()
    const TypeStatusLabel = TypeStack.addText(data.data.bzclxx[0].bzxx[0].jjzzlmc)
    TypeStatusLabel.font = Font.semiboldSystemFont(20)
    TypeStatusLabel.textColor = Color.white()
    TypeStack.addSpacer(15)

    let PeriodValidityStack = column0.addStack()
    PeriodValidityStack.layoutVertically()
    const PeriodValidityStatusLabel = PeriodValidityStack.addText(data.data.bzclxx[0].bzxx[0].yxqs + "~" +  data.data.bzclxx[0].bzxx[0].yxqz)
    PeriodValidityStatusLabel.font = Font.boldSystemFont(12)
    PeriodValidityStatusLabel.textColor = Color.black()
    PeriodValidityStack.addSpacer(5)

    let StateStack = column0.addStack()
    StateStack.layoutVertically()
    const StateLable = StateStack.addText(data.data.bzclxx[0].bzxx[0].blztmc)
    StateLable.font = Font.boldRoundedSystemFont(13)
    StateLable.textColor = Color.gray()
    StateStack.addSpacer(5)

    let ApplicationDateStack = column0.addStack()
    ApplicationDateStack.layoutVertically()
    const ApplicationDateLable = ApplicationDateStack.addText("申请时间: " + data.data.bzclxx[0].bzxx[0].sqsj.split(" ")[0])
    ApplicationDateLable.font = Font.regularSystemFont(13)
    ApplicationDateStack.addSpacer(5)

    let PlateNumStack = column0.addStack()
    PlateNumStack.layoutVertically()
    PlateNumStack.backgroundColor = Color.gray()
    const PlateNumStatusLabel = PlateNumStack.addText("车牌号: " + data.data.bzclxx[0].hphm)
    PlateNumStatusLabel.font = Font.regularSystemFont(13)

    const column1 = wrap.addStack()
    column1.layoutVertically()

    let WeatherStack = column1.addStack()
    WeatherStack.layoutVertically()
    let WeatherData = await getWeather()
    if (WeatherData.data.forecast[0].type == "霾") {
        weatherIcon = "🌫️"
    } else if (WeatherData.data.forecast[0].type == "雨") {
        weatherIcon = "🌧️"
    } else if (WeatherData.data.forecast[0].type == "晴") {
        weatherIcon = "☀️"
    } else if (WeatherData.data.forecast[0].type == "多云") {
        weatherIcon = "☁️"
    } else if (WeatherData.data.forecast[0].type == "阴") {
        weatherIcon = "⛅"
    } else {
        weatherIcon = WeatherData.data.forecast[0].type
    }
    const WeatherStatusLabel = WeatherStack.addText(WeatherData.cityInfo.city + " " + WeatherData.data.wendu + "° " + WeatherData.data.forecast[0].fx + WeatherData.data.forecast[0].fl + " " + weatherIcon)
    WeatherStatusLabel.font = Font.regularSystemFont(13)
    WeatherStatusLabel.textColor = Color.black()
    WeatherStack.addSpacer(20)

    let CarStack = column1.addStack()
    CarStack.setPadding(10, 10, 0, 0)
    let imgUrl = "https://p.ipic.vip/h4k1k5.png"
    const icon = await getImage(imgUrl)
    const iconImg = CarStack.addImage(icon)
    CarStack.addSpacer(8)
    return w
}

async function getImage(url) {
    let req = new Request(url)
    return await req.loadImage()
}

async function getData(url) {
    let req = new Request(url)
    // Authorization自行抓包
    let auth = ""
    req.method = "post"
    req.headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": auth
    }
    var data = await req.loadJSON()
    console.log(data)
    return data
}

async function getWeather() {
    // 以北京为例，其他城市自行搜索：https://betheme.net/news/txtlist_i84605v.html?action=onClick
    let cityID = "101010100"
    let req = new Request("http://t.weather.itboy.net/api/weather/city/" + cityID)
    req.method = "get"
    var data = await req.loadJSON()
    console.log(data)
    return data
}