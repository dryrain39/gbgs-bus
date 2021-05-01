from bus.fetch import *
from cache import cached_get_bus_line_node_list
import operator


# dict 안에서 요소에 맞는 인덱스 반환
def find_in_list(dictionary_list, key, value):
    idx = None
    element = None
    for i, e in enumerate(dictionary_list):
        if e.get(key, Exception) == value:
            idx = i
            element = e
            break

    return idx, element


# 차 번호를 이용하여 노선의 방향을 반환한다.
def get_bus_direction(car_no, line_node_list):
    for car in line_node_list["forwardPosition"] + line_node_list["reversePosition"]:
        if car_no == car["CARNO"]:
            return car["BUSDIRECTCD"]

    return None



# 버스 실시간 위치(forwardPosition, ReversePosition)와 특정 정류장 사이의 거리를 계산한다.
def get_bus_position_offset_from_node(bus_stop_id, line_node_list, write_lck=True):
    # Station 에 bus_stop_id 가 존재하는지 여부를 검사
    # Position 를 순회, 특정 정류장 사이 거리 계산.
    station_idx = {"forward": 0, "reverse": 0}
    station_idx["forward"], f_s_element = find_in_list(line_node_list["forwardStation"], "BUSSTOPID", bus_stop_id)
    station_idx["reverse"], r_s_element = find_in_list(line_node_list["reverseStation"], "BUSSTOPID", bus_stop_id)
    offset_list = {
        "forward": [],
        "reverse": []
    }

    proceed_bus_no = set()
    for bus in line_node_list["forwardPosition"] + line_node_list["reversePosition"]:
        # 버스 포지션 알아내기
        bus_pos = "forward" if bus["BUSDIRECTCD"] == "1" else "reverse"

        # 정방향, 역방향 정류장에 찾는 정류장이 없으면 건너뜀
        # 이미 검사한 버스면 건너뜀
        if station_idx[bus_pos] is None or bus["BUSID"] in proceed_bus_no:
            continue

        bus_idx = None
        tries = 5
        while bus_idx is None and tries > 0:
            bus_idx, bus_station = find_in_list(line_node_list[f"{bus_pos}Station"], "NODEORDER",
                                                int(bus["NODER"]) - (5 - tries))
            tries -= 1

        if tries != 4:
            print(line_node_list[f"{bus_pos}Station"], bus, tries)

        if bus_idx is None:
            continue

        if not write_lck:
            bus["edited"] = True
            bus["offset"] = bus_idx - station_idx[bus_pos]
            bus["bus_stop_name"] = bus_station["BUSSTOPNAME"]
            bus["to_bus_stop"] = line_node_list[f"{bus_pos}Station"][-1]

        # 리스트에 오프셋 추가
        offset_list[bus_pos].append(bus_idx - station_idx[bus_pos])

        # proceed bus 에 버스 추가
        proceed_bus_no.add(bus["BUSID"])

    return offset_list


# 특정 정류장의 모든 버스 실시간 위치를 반환한다.
def get_all_bus_position_offset_related_bus_stop(bus_stop_id):
    bus_lines = get_bus_line_list(bus_stop_id)

    for bus_line in bus_lines["bus_line_list"]:
        node_list = cached_get_bus_line_node_list(bus_line["BUSLINEID"])
        get_bus_position_offset_from_node(bus_stop_id=bus_stop_id, line_node_list=node_list,
                                          write_lck=False)
        bus_line["node_list"] = node_list
        del bus_line["node_list"]["forwardStation"]
        del bus_line["node_list"]["reverseStation"]

    return bus_lines


# 특정 정류장의 모든 버스 실시간 위치를 반환한다.
def get_all_b_p_pretty_json(bus_stop_id, skip_last_station=False):
    bus_positions = get_all_bus_position_offset_related_bus_stop(bus_stop_id)

    for bus_line in bus_positions["bus_line_list"]:
        bus_line["bus_positions"] = []
        for bus in bus_line["node_list"]["forwardPosition"] + bus_line["node_list"]["reversePosition"]:
            if "edited" not in bus.keys() or bus["edited"] is not True:
                continue

            # 이미 지나간 버스는 건너뜀
            if bus["offset"] > 0:
                continue

            # 검색 정류장과 종점이 일치할 경우 건너뜀.
            if skip_last_station is True and bus["to_bus_stop"]["BUSSTOPID"] == bus_stop_id:
                continue

            bus_line["bus_positions"].append(bus)

        # 정렬
        bus_line["bus_positions"].sort(key=operator.itemgetter('offset'), reverse=True)

        del bus_line["node_list"]

    return bus_positions


def get_all_b_p_pretty_text(bus_stop_id):
    bus_data = get_all_b_p_pretty_json(bus_stop_id, skip_last_station=True)

    before_text = {
        0: "출발",
        1: "전"
    }
    text = ""

    for bus in bus_data["bus_line_list"]:
        if len(bus["bus_positions"]) == 0:
            continue

        bus_side = f'\n{bus["BUSLINESIDE"]}' if bus["BUSLINESIDE"] is not None else ""

        bus_name = f"--- {bus['BUSLINENO']} 버스 ---{bus_side}"

        bus_position_list = []

        for idx, bus_position in enumerate(bus["bus_positions"]):
            # 최근 5개만 표시
            if idx >= 5:
                break

            # 0, 1, 전이면 도착, 전 으로 표시하게
            if abs(bus_position['offset']) in before_text.keys():
                b = before_text[idx]
            else:
                b = f"{abs(bus_position['offset'])}전"

            # 최근 2개의 도착 정보는 행선지를 표시하도록 함
            d = f'(종점: {bus_position["to_bus_stop"]["BUSSTOPNAME"]})' if idx < 2 else ""

            bus_position_list.append(f"{b}{d}")

        text += "\n".join([
            bus_name,
            ", ".join(bus_position_list)
        ]) + "\n"

    return text


if __name__ == '__main__':
    import logging
    import time

    logging.basicConfig(level=logging.DEBUG)

    d = time.time()
    # r = get_all_bus_position_offset_related_bus_stop("360020900")
    #
    import json

    #
    # print(json.dump(r, open("rd.json", "w", encoding="utf-8"), ensure_ascii=False))

    print(json.dumps(get_all_b_p_pretty_json("360005700", skip_last_station=True), ensure_ascii=False))
    print(get_all_b_p_pretty_text("360005700"))
    print(time.time() - d)