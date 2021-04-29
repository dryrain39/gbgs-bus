from diskcache import Cache
from bus.fetch import *

cache = Cache("./cache/")


def cached_get_bus_line_node_list(bus_line_id, hot_ttl=20, cold_ttl=170):
    bus_line_node_list = cache.get('get_bus_line_node_list_' + bus_line_id, None)
    if bus_line_node_list is None:
        bus_line_node_list = get_bus_line_node_list(bus_line_id=bus_line_id)

        if len(bus_line_node_list["forwardPosition"]) + len(bus_line_node_list["reversePosition"]) > 0:
            ttl = hot_ttl
        else:
            ttl = cold_ttl

        cache.set('get_bus_line_node_list_' + bus_line_id, bus_line_node_list, expire=ttl)

    return bus_line_node_list
