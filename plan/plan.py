#! /usr/bin/env python3

import html
import json
import datetime
import sys
from flask import Flask, render_template, request

# App config.
DEBUG = True
application = Flask(__name__)

try: # python2 compatibility
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

@application.route("/", methods=['GET', 'POST'])
def hello():


    args = dict(request.args)

    table = ''
    with open('roommap.json', 'r') as f:
        room_map = json.loads(f.read())
    with open('roomplan.json', 'r') as f:
        room_plan = json.loads(f.read())
    if len(args) == 0 or 'building' not in args or 'room_type' not in args:
        args['building'] = room_map.keys()
        args['room_type'] = room_map[list(room_map.keys())[0]].keys()
    rooms = {}
    search_for_buildings = args['building']
    search_for_rooms = args['room_type']
    for building in search_for_buildings:
        rooms[building] = []
        for room in search_for_rooms:
            rooms[building] += room_map[building][room]
    weekday = min(datetime.date.today().weekday(), 4)
    times = ['vor 8', '8','9','10','11','12','13','14','15','16','17','18','19','ab  20']
    current_time = datetime.datetime.now().hour
    current_time = times[0] if current_time < 8 else (times[-1] if current_time > 20 else str(current_time))
    for building in rooms:
        table += '<table width="100%"><col width="140"><tr><th><strong>{}</strong></th>'.format(building)
        for time in times:
            time = time.split(' ')[-1]+'+' if 'ab ' in time else time
            time = time.replace('vor ', '<')
            # table += '<th>{}</th>'.format(time)
            table += '<th{}>{}</th>'.format(' class="now"' if current_time == time else '', time)
        for room in rooms[building]:
            table += '<tr>'
            table += '<td><strong>{}</strong></td>'.format(room)
            for time in times:
                free = not False in [i[weekday] for i in room_plan[time][room]]
                table += '<td class="{}{}">'.format('free' if free else 'taken', ' now' if current_time == time else '')
            table += '</tr>'
        table += '</table>'

        
    with open('roommap.json', 'r') as f:
        rooms = json.loads(f.read())
    buildings = {html.escape(i): i in args['building'] for i in rooms.keys()}
    room_types = []
    for building in rooms:
        for room_type in rooms[building]:
            if not room_type in room_types:
                room_types.append(room_type)
    room_types = {html.escape(i): i in args['room_type'] for i in room_types}
    weekday_text = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'][weekday]
    return render_template('hello.html', room_types = room_types, buildings = buildings, table = table, weekday = weekday_text)


if __name__ == "__main__":
    application.run(debug=True, port=5000)
