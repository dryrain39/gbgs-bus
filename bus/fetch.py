import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/74.0.3729.169 Safari/537.36",
    "Accept-Language": "ko",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
}


# 버스 정류장 검색
# return: [{'GISY_5181': 268203.84577646, 'BUSSTOPID': '360020900', 'NGISX': 186597.4609, 'NGISY': 266639.5584,
#           'BUSSTOPNAME': '대구대종점', 'GISX_5181': 367156.93516694}]
def search_bus_stop(keyword: str):
    r = requests.post("http://its.gbgs.go.kr/bus/getBusstopList/", headers=headers, data={
        "BUSSTOPID": keyword
    })

    response_json = r.json()

    if response_json["success"] is not True:
        raise RequestFailError(f"search_bus_stop {keyword}")

    return response_json["result"]


# 버스 노선 조회(도착정보, 정류장을 경유하는 노선 조회)
# 'bus_line_list': [{'BUSLINEKINDCD': '01', 'BUSLINENO': '399', 'BUSLINEID': '360084161',
#                    'CNT': 1, 'BUSLINESIDE': '자인->평사->하양->골프장,속초->자인'},
# 'bus_arrive_list': [{'BUSSTOPGAP': 1, 'NOWBUSBUSSTOPID': '360052536', 'BUSLINENO': '818(대구대)',
#                      'INX': '01', 'TIMEGAP': '전', 'PREDICTTIME': '20210429154006', 'CARTERMID': '36027438',
#                      'NOWBUSSTOPNAME': '출발', 'BUSSTOPID': '360020900', 'LINESIDELENGTH': 3,
#                      'BUSSTOPNAME': '대구대종점', 'BUSLINESIDE': '(대구대)'},
def get_bus_line_list(bus_stop_id: str):
    r = requests.post("http://its.gbgs.go.kr/bus/getBusLineList/", headers=headers, data={
        "type": "busstation",
        "value1": bus_stop_id,
    })

    response_json = r.json()

    if response_json["success"] is not True:
        raise RequestFailError(f"get_bus_line_list {bus_stop_id}")

    return {
        "bus_line_list": response_json["result"]["busLineList"],
        "bus_arrive_list": response_json["result"]["busArriveList"],
    }
    pass


# 버스 운행 정보 조회
def get_bus_line_information(bus_line_id: str):
    r = requests.post("http://its.gbgs.go.kr/bus/getBusLineInfo/", headers=headers, data={
        "p_BusLineID": bus_line_id,
    })

    response_json = r.json()

    if response_json["success"] is not True:
        raise RequestFailError(f"get_bus_line_information {bus_line_id}")

    return {
        "bus_line_no": response_json["result"][0]["BUSLINENO"],
        "bus_line_side": response_json["result"][0]["BUSLINESIDE"],
        "start_bus_stop_name": response_json["result"][0]["STARTBUSSTOPNAME"],
        "end_bus_stop_name": response_json["result"][0]["ENDBUSSTOPNAME"],
        "total_bus_stop_count": response_json["result"][0]["PATHBUSSTOPCNT"],
    }
    pass


# 버스 실시간 정보 조회
# 'forwardPosition': [{'NODER': 1, 'BUSID': '081909', 'BUSDIRECTCD': '1', 'RCVTIME': '20210429162519',
#                      'GISY_5181': None, 'BUSSTOPID': '360054800', 'NGISX': 181860.7624, 'NGISY': 267756.9926,
#                      'BUSTYPE': 'N', 'CARNO': '1909', 'NODEID': '3609554800', 'GISX_5181': None},
# "forwardStation": [{"NODEORDER": 1, "GISY_5181": null, "BUSSTOPID": "360054800", "NGISX": 181860.7624,
#                     "NGISY": 267756.9926, "BUSSTOPNAME": "경일대종점", "GISX_5181": null },
def get_bus_line_node_list(bus_line_id: str):
    r = requests.post("http://its.gbgs.go.kr/bus/getBusLineNodeList/", headers=headers, data={
        "BUSLINEID": bus_line_id,
    })

    response_json = r.json()

    if response_json["success"] is not True:
        raise RequestFailError(f"get_bus_line_node_list {bus_line_id}")

    return {
        'forwardPosition': response_json["result"]["forwardPosition"],
        "reversePosition": response_json["result"]["reversePosition"],
        "forwardStation": response_json["result"]["forwardStation"],
        "reverseStation": response_json["result"]["reverseStation"],
    }


class RequestFailError(Exception):
    def __init__(self, location):
        super().__init__("success 코드가 True가 아닙니다: " + location)


if __name__ == '__main__':
    import json
    print(json.dumps(get_bus_line_node_list("3000840000")))
