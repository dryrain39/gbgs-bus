import operator

from bus.fetch import get_bus_line_list
from cache import cached_get_bus_line_node_list
from tools import get_all_bus_position_offset_related_bus_stop, get_bus_position_offset_from_node


# 특정 정류장의 모든 버스 실시간 위치를 반환한다.
def flask_get_all_bus_position_offset_related_bus_stop(bus_stop_id, socket_io=None):
    bus_lines = get_bus_line_list(bus_stop_id)

    for bus_line in bus_lines["bus_line_list"]:
        try:
            node_list = cached_get_bus_line_node_list(bus_line["BUSLINEID"])
        except Exception as e:
            print(e)
            continue

        if socket_io is not None:
            socket_io.emit("load_msg", {
                "func": "get_bus_position_offset_from_node",
                "bus_stop_id": bus_stop_id,
                "bus_line_id": bus_line["BUSLINEID"],
                "bus_line_name": bus_line["BUSLINENO"],
                "bus_line_side": bus_line["BUSLINESIDE"],
            })
            socket_io.sleep(.01)
        get_bus_position_offset_from_node(bus_stop_id=bus_stop_id, line_node_list=node_list,
                                          write_lck=False)
        bus_line["node_list"] = node_list
        del bus_line["node_list"]["forwardStation"]
        del bus_line["node_list"]["reverseStation"]

    return bus_lines


# 특정 정류장의 모든 버스 실시간 위치를 반환한다.
def flask_get_all_bus_position(bus_stop_id, skip_last_station=False, socket_io=None):
    bus_positions = flask_get_all_bus_position_offset_related_bus_stop(bus_stop_id, socket_io)

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
