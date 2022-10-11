carousel_template = {
    "type": "template",
    "altText": "找到美食囉！",
    "template": {
        "type": "carousel",
        "columns": [
            {
                "thumbnailImageUrl": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
                "title": "店名",
                "text": "店家地址和營業時間",
                "actions": [
                    {
                        "type": "uri",
                        "label": "查看地圖",
                        "uri": "https://www.google.com.tw/maps"
                    }
                ]
            }
        ]
    }
}

buttons_template = {
    "type": "template",
    "altText": "的詳細資訊",
    "template": {
        "type": "buttons",
        # "thumbnailImageUrl": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
        # "title": "店名",
        "text": "詳細資訊",
        "actions": [
            {
                "type": "uri",
                "label": "查看地圖",
                "uri": "url"
            }
        ]
    }
}

flex_message = {
    "type": "carousel",
    "contents": [
        {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "label": "Line",
                    "uri": "https://linecorp.com/"
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "[店名]",
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True,
                        "contents": []
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "地址",
                                        "size": "xs",
                                        "color": "#AAAAAA",
                                        "flex": 1,
                                        "contents": []
                                    },
                                    {
                                        "type": "text",
                                        "text": "",
                                        "size": "xs",
                                        "color": "#666666",
                                        "flex": 3,
                                        "wrap": True,
                                        "contents": []
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "電話",
                                        "size": "xs",
                                        "color": "#AAAAAA",
                                        "flex": 1,
                                        "contents": []
                                    },
                                    {
                                        "type": "text",
                                        "text": "",
                                        "size": "xs",
                                        "color": "#666666",
                                        "flex": 3,
                                        "contents": []
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "營業時間",
                                        "size": "xs",
                                        "color": "#AAAAAA",
                                        "flex": 1,
                                        "contents": []
                                    },
                                    {
                                        "type": "text",
                                        "text": "",
                                        "size": "xs",
                                        "color": "#666666",
                                        "flex": 3,
                                        "wrap": True,
                                        "contents": []
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "平均價位",
                                        "size": "xs",
                                        "color": "#AAAAAA",
                                        "flex": 1,
                                        "contents": []
                                    },
                                    {
                                        "type": "text",
                                        "text": "$",
                                        "size": "xs",
                                        "color": "#666666",
                                        "flex": 3,
                                        "contents": []
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "地圖評分",
                                        "size": "xs",
                                        "color": "#AAAAAA",
                                        "flex": 1,
                                        "contents": []
                                    },
                                    {
                                        "type": "text",
                                        "text": "",
                                        "size": "xs",
                                        "color": "#666666",
                                        "flex": 3,
                                        "contents": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "flex": 0,
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "菜單",
                            "uri": "https://linecorp.com"
                        },
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "地圖",
                            "uri": "https://linecorp.com"
                        },
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "聯絡店家",
                            "uri": "https://linecorp.com"
                        },
                        "height": "sm"
                    },
                    {
                        "type": "spacer",
                        "size": "sm"
                    }
                ]
            }
        }
    ]
}
