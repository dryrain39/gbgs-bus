from gevent import monkey

monkey.patch_all()

from flask import Flask, request, abort, redirect

from bus.fetch import search_bus_stop
from tools2 import flask_get_all_bus_position
from flask_socketio import SocketIO
from cache import cached_all_bus_stop

app = Flask(__name__, static_url_path='', static_folder='html')
socket_io = SocketIO(app)


@app.route('/bus.json')
def bus():
    try:
        socket_io.emit("ping", "hello")
        return flask_get_all_bus_position(request.args.get('bus_stop'), skip_last_station=True,
                                          socket_io=socket_io)
    except:
        abort(500)


@app.route('/search.json')
def search():
    try:
        return {"result": search_bus_stop(request.args.get('keyword'))}
    except:
        abort(500)


@app.route('/all_bus_stop.json')
def all_bus_stop():
    try:
        return {"result": cached_all_bus_stop()}
    except:
        abort(500)


@app.route('/')
def hello():
    return redirect('index.html')


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)
    socket_io.run(app=app, debug=False, host="0.0.0.0")
