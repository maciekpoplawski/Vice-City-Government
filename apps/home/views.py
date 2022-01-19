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
        "img": '/static/assets/img/cars/200_patriot.jpg',
        "category": "military",
    },
    163: {
        "name": "Barracks",
        "img": '/static/assets/img/cars/163_barracks.jpg',
        "category": "military",
    },
    185: {
        "name": "Flatbed",
        "img": '/static/assets/img/cars/185_flatbed.jpg',
        "category": "truck",
    },
    135: {
        "name": "Sentinel",
        "img": '/static/assets/img/cars/135_sentinel.jpg',
        "category": "sedan",
    },
    174: {
        "name": "Sentinel XS",
        "img": '/static/assets/img/cars/174_sentxs.jpg',
        "category": "sedan",
    },
    172: {
        "name": "Romero's Hearse",
        "img": '/static/assets/img/cars/172_romero.jpg',
        "category": "hearse",
    },
    224: {
        "name": "Hotring Racer",
        "img": '/static/assets/img/cars/224_hotring.jpg',
        "category": "sports_car",
    },
    131: {
        "name": "Idaho",
        "img": '/static/assets/img/cars/131_idaho.jpg',
        "category": "two_door",
    },
}

