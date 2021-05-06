from diskcache import Cache
from bus.fetch import *
import logging

cache = Cache("./cache/")


def cached_get_bus_line_node_list(bus_line_id, hot_ttl=20, cold_ttl=170):
    bus_line_node_list = cache.get('get_bus_line_node_list_' + bus_line_id, None)
    if bus_line_node_list is None:
        bus_line_node_list = get_bus_line_node_list(bus_line_id=bus_line_id)

        position_count = len(bus_line_node_list["forwardPosition"]) + len(bus_line_node_list["reversePosition"])

        if position_count > 0:
            logging.debug("set hot ttl" + str(position_count))
            ttl = hot_ttl
        else:
            logging.debug("set cold ttl" + str(position_count))
            ttl = cold_ttl

        cache.set('get_bus_line_node_list_' + bus_line_id, bus_line_node_list, expire=ttl)

    return bus_line_node_list


def cached_all_bus_stop(cold_ttl=604800):  # 604800=1w
    all_bus_stop = cache.get('all_bus_stop', None)
    if all_bus_stop is None:
        all_bus_stop = search_bus_stop(keyword="%%")
        all_bus_stop = sorted(list(map(lambda x: x["BUSSTOPNAME"], all_bus_stop)))

        cache.set('all_bus_stop', all_bus_stop, expire=cold_ttl)

    return all_bus_stop
