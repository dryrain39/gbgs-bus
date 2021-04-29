from bus.fetch import *
from cache import cached_get_bus_line_node_list


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
        logging.debug(bus_line["BUSLINEID"])
        logging.debug(bus_line["BUSLINENO"])
        get_bus_position_offset_from_node(bus_stop_id="360020900", line_node_list=node_list,
                                          write_lck=False)
        bus_line["node_list"] = node_list
        del bus_line["node_list"]["forwardStation"]
        del bus_line["node_list"]["reverseStation"]

    return bus_lines


if __name__ == '__main__':
    import logging
    import time

    logging.basicConfig(level=logging.DEBUG)

    d = time.time()
    r = get_all_bus_position_offset_related_bus_stop("360020900")
    print(time.time() - d)
    import json

    print(json.dump(r, open("rd.json", "w", encoding="utf-8"), ensure_ascii=False))

