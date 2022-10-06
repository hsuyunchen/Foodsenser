from flask import Flask, request, make_response, jsonify
import googlemaps
from Lib.packages.messages import carousel_template
import copy
from time import sleep, time as current_time
from datetime import datetime, timezone, timedelta
from threading import Thread
from operator import itemgetter
import os

app = Flask(__name__)
api_key = "AIzaSyCRxSP4yhIw6D4REozENkrFZWOTVBD_Nk4"
gmaps = googlemaps.Client(key=api_key)
global start_time


@app.route('/', methods=['POST'])
def webhook():
    global start_time
    start_time = current_time()
    try:
        req = request.get_json()
    except AttributeError:
        return "json error"

    res = search(req)

    if type(res) != dict:
        return make_response(jsonify({"fulfillmentMessages": [{"platform": "LINE", "text": {"text": [res]}}]}))
    elif "followupEventInput" in res:
        return make_response(jsonify(res))
    else:
        return make_response(jsonify({"fulfillmentMessages": [{"platform": "LINE", "payload": {"line": res}}]}))


def search(req):
    if "action" in req['queryResult']:
        place = req['queryResult']['outputContexts'][0]['parameters']['place'].replace("美食", "")
        store = req['queryResult']['outputContexts'][0]['parameters']['store']
        day = req['queryResult']['outputContexts'][0]['parameters']['day']
        time = req['queryResult']['outputContexts'][0]['parameters']['time'] if req['queryResult']['outputContexts'][0]['parameters']['time'] != "現在" else ""
        food = req['queryResult']['outputContexts'][0]['parameters']['food']
    else:
        place = req['queryResult']['parameters']['place'].replace("美食", "")
        store = req['queryResult']['parameters']['store']
        day = req['queryResult']['parameters']['day']
        time = req['queryResult']['parameters']['time'] if req['queryResult']['parameters']['time'] != "現在" else ""
        food = req['queryResult']['parameters']['food']

    tz = timezone(timedelta(hours=+8))
    today = datetime.today().astimezone(tz)
    if day == "" or day == "今天":
        weekday = today.weekday()
    elif day == "明天":
        weekday = (today.weekday() + 1) % 7
    elif day == "後天":
        weekday = (today.weekday() + 2) % 7
    elif day == "大後天":
        weekday = (today.weekday() + 3) % 7
    elif day == "昨天":
        weekday = (today.weekday() - 1) % 7
    elif day == "前天":
        weekday = (today.weekday() - 2) % 7
    elif day == "大前天":
        weekday = (today.weekday() - 3) % 7
    elif day == "週一":
        weekday = 0
    elif day == "週二":
        weekday = 1
    elif day == "週三":
        weekday = 2
    elif day == "週四":
        weekday = 3
    elif day == "週五":
        weekday = 4
    elif day == "週六":
        weekday = 5
    elif day == "週日":
        weekday = 6
    elif "號" in day:
        if day == "30號" and today.month == 2:
            return "2月沒有30號喔！"
        elif day == "31號" and (today.month == 2 or today.month == 4 or today.month == 6 or today.month == 9 or today.month == 11):
            return "這個月沒有31號喔！"
        elif int(day[:-1]) < today.day:
            next_month = today.month + 1 if today.month != 12 else 1
            if day == "30號" and next_month == 2:
                return "2月沒有30號喔！"
            elif day == "29號" and next_month == 2:
                if today.year % 4 != 0 or (today.year % 100 == 0 and today.year % 400 != 0):
                    return "今年2月沒有29號喔！"
            year = today.year + 1 if today.month == 12 else today.year
            weekday = datetime.strptime(str(year) + "-" + str(next_month) + "-" + day[:-1], "%Y-%m-%d").weekday()
        else:
            if day == "29號" and today.month == 2:
                if today.year % 4 != 0 or (today.year % 100 == 0 and today.year % 400 != 0):
                    return "今年2月沒有29號喔！"
            year = today.year
            month = today.month
            weekday = datetime.strptime(str(year) + "-" + str(month) + "-" + day[:-1], "%Y-%m-%d").weekday()
    elif "-" in day:
        if day < today.strftime("%m-%d"):
            next_year = today.year + 1
            weekday = datetime.strptime(str(next_year) + "-" + day, "%Y-%m-%d").weekday()
        else:
            current_year = today.year
            weekday = datetime.strptime(str(current_year) + "-" + day, "%Y-%m-%d").weekday()
    else:
        return "您想在哪一天吃呢？\n（日期請以一天為單位重新查詢）"

    # place without store, day, time, food
    if store == "" and day == "" and time == "" and food == "":
        result = gmaps.places(query=place + "美食", language="zh-TW", region="tw", open_now=True)
    # place, store without day, time, do not care food
    elif store != "" and day == "" and time == "":
        result = gmaps.places(query=place + store, language="zh-TW", region="tw", open_now=True)
    # place, day/time without store, food
    elif store == "" and (day != "" or time != "") and food == "":
        result = gmaps.places(query=place + "美食", language="zh-TW", region="tw")
    # place, food without store, day, time
    elif store == "" and day == "" and time == "" and food != "":
        result = gmaps.places(query=place + food, language="zh-TW", region="tw", open_now=True)
    # place, store, day/time, do not care food
    elif store != "" and (day != "" or time != ""):
        result = gmaps.places(query=place + store, language="zh-TW", region="tw")
    # place, day/time, food without store
    else:  # store == "" and (day != "" or time != "") and food != ""
        result = gmaps.places(query=place + food, language="zh-TW", region="tw")

    if result['status'] == "ZERO_RESULTS":
        return "對不起，目前沒有營業中的店家😥\n試試其他關鍵字或指定時段吧！"

    if "next_page_token" in result:
        sleep(1.8)
        try:
            more_results = gmaps.places(page_token=result['next_page_token'])
        except googlemaps.exceptions.ApiError:
            more_results = {"results": {}}
        for i in range(len(more_results['results'])):
            result['results'].append(more_results['results'][i])

    if (current_time() - start_time) > 3.3:
        return {"followupEventInput": {
            "name": "extend_webhook_deadline",
            "languageCode": "zh-TW",
            "parameters": {
                "place": place,
                "food": food,
                "day": day,
                "time": time,
                "store": store
            }
        }}

    i = 0
    while i < len(result['results']):
        if "business_status" in result['results'][i] and result['results'][i]['business_status'] != "OPERATIONAL":
            del result['results'][i]
            continue
        if "夜市" not in food and "飲料" not in food and "types" in result['results'][i]:
            if "food" not in result['results'][i]['types'] and "bar" not in result['results'][i]['types']:
                del result['results'][i]
                continue
        i += 1

    res_msg = copy.deepcopy(carousel_template)
    del res_msg['template']['columns'][0]
    if len(result['results']) != 0:
        threads = []
        for i in range(len(result['results'])):
            res_msg["template"]["columns"].append(copy.deepcopy(carousel_template["template"]["columns"][0]))
            threads.append(Thread(target=response, args=(i, res_msg, result, weekday, time)))
            threads[-1].start()
        for t in threads:
            t.join()

        if "縣" not in place and "市" not in place and "鄉" not in place and "鎮" not in place and "區" not in place and "路" not in place:
            index = res_msg['template']['columns'][0]['text'].find("市")
            if index == -1:
                res_msg['template']['columns'][0]['text'].find("縣")
            place = res_msg['template']['columns'][0]['text'][index - 2:index + 1]
        i = 0
        while i < len(res_msg['template']['columns']):
            if "休息" in res_msg['template']['columns'][i]['text']:
                del res_msg['template']['columns'][i]
                continue
            if "未提供營業時間" in res_msg['template']['columns'][i]['text'] and time != "":
                del res_msg['template']['columns'][i]
                continue
            if place not in res_msg['template']['columns'][i]['text']:
                del res_msg['template']['columns'][i]
                continue
            i += 1

        res_msg['template']['columns'].sort(key=itemgetter("text"), reverse=True)
        if "action" in req['queryResult']:
            if "lifespanCount" not in req['queryResult']['outputContexts'][0]:
                if len(res_msg['template']['columns']) > 30:
                    res_msg['template']['columns'] = res_msg['template']['columns'][30:40]
                else:
                    return "沒有更多符合條件的美食了😥"
            elif req['queryResult']['outputContexts'][0]['lifespanCount'] == 1:
                if len(res_msg['template']['columns']) > 20:
                    res_msg['template']['columns'] = res_msg['template']['columns'][20:30]
                else:
                    return "沒有更多符合條件的美食了😥"
            else:
                if len(res_msg['template']['columns']) > 10:
                    res_msg['template']['columns'] = res_msg['template']['columns'][10:20]
                else:
                    return "沒有更多符合條件的美食了😥"
        else:
            res_msg['template']['columns'] = res_msg['template']['columns'][:10]

    if len(res_msg['template']['columns']) == 0:
        return "對不起，目前沒有相關資料😥\n試試其他關鍵字吧！"
    else:
        return res_msg


def response(i, res_msg, search_result, weekday, hour):
    address = search_result['results'][i]['formatted_address'].replace(" ", "")
    # 106台北市
    if address[5] == "市" or address[5] == "縣":
        address = address[3:]
    # 106大安區
    elif address[2] != "市" and address[2] != "縣" and (address[5] == "鄉" or address[5] == "鎮" or address[5] == "區"):
        address = address[3:]
    elif len(address) <= 7:
        pass
    # 10671台北市
    elif address[7] == "市" or address[7] == "縣" or address[7] == "鄉" or address[7] == "鎮" or address[7] == "區":
        address = address[5:]
    # 106320台北市
    elif address[8] == "市" or address[8] == "縣":
        address = address[6:]

    place_id = search_result['results'][i]['place_id']
    detail = gmaps.place(place_id, fields=["url", "opening_hours", "price_level", "rating"], language="zh-TW")
    rating = str(detail['result']['rating']) if "rating" in detail['result'] else ""
    if len(rating) == 1:
        rating += ".0"
    if len(rating) != 0:
        rating += "⭐"
    price = "\n"
    if "price_level" in detail['result']:
        price = "．"
        for j in range(int(detail['result']['price_level'])):
            price += "$"
        price += "\n"
    time = "未提供營業時間"
    if "opening_hours" in detail['result']:
        time = detail['result']['opening_hours']['weekday_text'][weekday].replace("星期", "週").replace(": ", "　")
        if hour != "":
            if "24 小時營業" in detail['result']['opening_hours']['weekday_text'][weekday]:
                opening = 1
            # ~6AM, 7:30AM~
            elif hour == "清晨":
                opening = 0
                day_hour = int(str((weekday + 1) % 7) + "0600")
                for j in detail['result']['opening_hours']['periods']:
                    if j['open']['day'] == (weekday + 1) % 7:
                        if j['open']['day'] != j['close']['day']:
                            if j['close']['day'] == 0:
                                j['close']['day'] = 7
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10000 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 130 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10130 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                        else:
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 130 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
            # ~9AM, 11AM~
            elif hour == "早上":
                opening = 0
                day_hour = int(str((weekday + 1) % 7) + "0900")
                for j in detail['result']['opening_hours']['periods']:
                    if j['open']['day'] == (weekday + 1) % 7:
                        if j['open']['day'] != j['close']['day']:
                            if j['close']['day'] == 0:
                                j['close']['day'] = 7
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10000 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 200 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10200 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                        else:
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 200 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
            # ~12PM, 1PM~
            elif hour == "中午":
                opening = 0
                day_hour = int(str((weekday + 1) % 7) + "1200")
                for j in detail['result']['opening_hours']['periods']:
                    if j['open']['day'] == (weekday + 1) % 7:
                        if j['open']['day'] != j['close']['day']:
                            if j['close']['day'] == 0:
                                j['close']['day'] = 7
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10000 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 100 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10100 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                        else:
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 100 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
            # ~2PM, 4PM~
            elif hour == "下午":
                opening = 0
                day_hour = int(str((weekday + 1) % 7) + "1400")
                for j in detail['result']['opening_hours']['periods']:
                    if j['open']['day'] == (weekday + 1) % 7:
                        if j['open']['day'] != j['close']['day']:
                            if j['close']['day'] == 0:
                                j['close']['day'] = 7
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10000 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 200 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10200 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                        else:
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 200 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
            # ~6PM, 9PM~
            elif hour == "晚上":
                opening = 0
                day_hour = int(str((weekday + 1) % 7) + "1800")
                for j in detail['result']['opening_hours']['periods']:
                    if j['open']['day'] == (weekday + 1) % 7:
                        if j['open']['day'] != j['close']['day']:
                            if j['close']['day'] == 0:
                                j['close']['day'] = 7
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10000 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 300 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10300 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                        else:
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 300 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
            # ~8PM, 11PM~
            elif hour == "夜晚":
                opening = 0
                day_hour = int(str((weekday + 1) % 7) + "2000")
                for j in detail['result']['opening_hours']['periods']:
                    if j['open']['day'] == (weekday + 1) % 7:
                        if j['open']['day'] != j['close']['day']:
                            if j['close']['day'] == 0:
                                j['close']['day'] = 7
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10000 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 300 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10300 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                        else:
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 300 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
            # ~12AM, 3AM~
            elif hour == "凌晨":
                opening = 0
                day_hour = int(str((weekday + 1) % 7) + "0000")
                for j in detail['result']['opening_hours']['periods']:
                    if j['open']['day'] == (weekday + 1) % 7:
                        if j['open']['day'] != j['close']['day']:
                            if j['close']['day'] == 0:
                                j['close']['day'] = 7
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10000 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 300 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10300 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                        else:
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 300 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
            else:
                opening = 0
                day_hour = int(str((weekday + 1) % 7) + hour)
                for j in detail['result']['opening_hours']['periods']:
                    if j['open']['day'] == (weekday + 1) % 7:
                        if j['open']['day'] != j['close']['day']:
                            if j['close']['day'] == 0:
                                j['close']['day'] = 7
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                            elif int(str(j['open']['day']) + j['open']['time']) <= day_hour + 10000 <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
                        else:
                            if int(str(j['open']['day']) + j['open']['time']) <= day_hour <= int(
                                    str(j['close']['day']) + j['close']['time']):
                                opening = 1
                                break
            if opening == 0:
                time = "休息"

    res_msg['template']['columns'][i]['title'] = search_result['results'][i]['name'][:40]
    res_msg['template']['columns'][i]['text'] = (rating + price + time + "\n" + address[:22])[:60]
    res_msg['template']['columns'][i]['actions'][0]['uri'] = detail['result']['url']
    if "photos" in search_result['results'][i] and time != "休息":
        photo_ref = search_result['results'][i]['photos'][0]['photo_reference']
        photo = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=" + photo_ref + \
                "&key=" + api_key
        res_msg['template']['columns'][i]['thumbnailImageUrl'] = photo


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
