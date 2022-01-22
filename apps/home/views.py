# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template import loader
from django.urls import reverse


# set async_mode to 'threading', 'eventlet', 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's
# installed
async_mode = 'threading'

import os

from django.http import HttpResponse
import socketio

basedir = os.path.dirname(os.path.realpath(__file__))
sio = socketio.Server(async_mode=async_mode)
thread = None


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        sio.sleep(10)
        count += 1
        sio.emit('my_response', {'data': 'Server generated event'},
                 namespace='/test')


@sio.event
def my_event(sid, message):
    sio.emit('my_response', {'data': message['data']}, room=sid)


@sio.event
def create_car(sid, message):
    sio.emit('create_car_by_id', {'car_id': message['car_id'], 'player_name': message['player_name']})


@sio.event
def join(sid, message):
    sio.enter_room(sid, message['room'])
    sio.emit('my_response', {'data': 'Entered room: ' + message['room']},
             room=sid)


@sio.event
def leave(sid, message):
    sio.leave_room(sid, message['room'])
    sio.emit('my_response', {'data': 'Left room: ' + message['room']},
             room=sid)


@sio.event
def close_room(sid, message):
    sio.emit('my_response',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'])
    sio.close_room(message['room'])


@sio.event
def my_room_event(sid, message):
    sio.emit('my_response', {'data': message['data']}, room=message['room'])


@sio.event
def disconnect_request(sid):
    sio.disconnect(sid)


@sio.event
def connect(sid, environ):
    sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)


@sio.event
def disconnect(sid):
    print('Client disconnected')


# import socket
#
# soketnik = socket.socket()
# host = socket.gethostname()
# port = 12221
#
# soketnik.connect((host, port))
# print('Connected to ' + host)


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index3.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def cars_postaw_kloca(request):
    context = {'segment': 'index'}

    # mesedz = "PIERDOL SIE"
    # soketnik.send(mesedz.encode(encoding='utf8'))

    html_template = loader.get_template('home/cars-test.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def sockets_test(request):
    context = {'segment': 'index'}
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)

    html_template = loader.get_template('home/sockets-sample.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def spawn_car(request):
    context = {
        'segment': 'index',
        'cars_data': CAR_INFO
    }
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)

    html_template = loader.get_template('home/cars-gallery.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def create_car_from_store(request):
    car_id = request.GET.get("car_id")

    car_info = get_car_info(int(car_id))
    if not car_info:
        return HttpResponseNotFound("No such car. Please go fuck yourself.")

    context = {
        'segment': 'index',
        'car_img_link': car_info.get("img"),
        'car_name': car_info.get("name"),
        'car_id': int(car_id)
    }

    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)

    html_template = loader.get_template('home/create-car.html')
    return HttpResponse(html_template.render(context, request))


def get_car_info(car_id):
    return CAR_INFO.get(car_id)


CAR_INFO = {
    200: {
        "name": "Patriot",
        "img": '/static/assets/img/cars/200.jpg',
        "category": "utility",
    },
    163: {
        "name": "Barracks",
        "category": "utility",
    },
    185: {
        "name": "Flatbed",
        "category": "truck",
    },
    135: {
        "name": "Sentinel",
        "category": "sedan",
    },
    174: {
        "name": "Sentinel XS",
        "category": "sedan",
    },
    172: {
        "name": "Romero's Hearse",
        "category": "utility",
    },
    224: {
        "name": "Hotring Racer",
        "category": "sports_car",
    },
    131: {
        "name": "Idaho",
        "category": "two_door",
    },
    149: {
        "name": "Esperanto",
        "category": "two_door",
    },
    201: {
        "name": "Love Fist",
        "category": "stretch",
    },
    139: {
        "name": "Stretch",
        "category": "stretch",
    },
    168: {
        "name": "Cabbie",
        "category": "taxi",
    },
    216: {
        "name": "Kaufman Cab",
        "category": "taxi",
    },
    188: {
        "name": "Zebra Cab",
        "category": "taxi",
    },
    208: {
        "name": "Walton",
        "category": "pickup",
    },
    148: {
        "name": "Moonbeam",
        "category": "van",
    },
    142: {
        "name": "Voodoo",
        "category": "lowrider",
    },
    219: {
        "name": "Rancher",
        "category": "offroad",
    },
    134: {
        "name": "Perennial",
        "category": "station_wagon",
    },
    159: {
        "name": "Banshee",
        "category": "sports_car",
    },
    232: {
        "name": "Hotring Racer",
        "category": "sports_car",
    },
    233: {
        "name": "Hotring Racer",
        "category": "sports_car",
    },
    225: {
        "name": "Sandking",
        "category": "offroad",
    },
    153: {
        "name": "Mr. Whoopee",
        "category": "van",
    },
    220: {
        "name": "FBI Rancher",
        "category": "offroad",
    },
    222: {
        "name": "Greenwood",
        "category": "sedan",
    },
    215: {
        "name": "Baggage Handler",
        "category": "fun",
    },
    187: {
        "name": "Caddy",
        "category": "fun",
    },
    211: {
        "name": "Deluxo	",
        "category": "sports_car",
    },
    234: {
        "name": "Bloodring Banger	",
        "category": "sports_car",
    },
    235: {
        "name": "Bloodring Banger",
        "category": "sports_car",
    },
    197: {
        "name": "Oceanic",
        "category": "sedan",
    },
    196: {
        "name": "Glendale",
        "category": "sedan",
    },
    212: {
        "name": "Burrito",
        "category": "van",
    },
    179: {
        "name": "Gang Burrito",
        "category": "van",
    },
    143: {
        "name": "Pony",
        "category": "van",
    },
    170: {
        "name": "Rumpo",
        "category": "van",
    },
    189: {
        "name": "Top Fun",
        "category": "van",
    },
    132: {
        "name": "Stinger",
        "category": "sport",
    },
    145: {
        "name": "Cheetah",
        "category": "sport",
    },
    236: {
        "name": "Cheetah Police",
        "category": "sport",
    },
    146: {
        "name": "Ambulance",
        "category": "utility",
    },
    144: {
        "name": "Mule",
        "category": "truck",
    },
    213: {
        "name": "Spand Express",
        "category": "van",
    },
    229: {
        "name": "Benson",
        "category": "van",
    },
    138: {
        "name": "Trashmaster",
        "category": "utility",
    },

}

