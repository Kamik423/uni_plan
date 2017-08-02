#! /usr/bin/env

import itertools
import urllib.request
from bs4 import BeautifulSoup


def search_url_from_id(gebid, raumartid = None):
    """
    returns the url for a search on the university website based on one building and one room type
    """
    template = 'https://www-sbhome1.zv.uni-wuerzburg.de/qisserver/rds?state=wsearchv&search=3&raum.gebid={}&P_start=0&P_anzahl=50&_form=display'
    url = template.format(gebid)
    if raumartid:
        url = '{}&k_raumart.raumartid={}'.format(url, raumartid)
    return url


def room_url_for_room_id(roomid):
    """
    room schedule url from room id
    """
    template = 'https://www-sbhome1.zv.uni-wuerzburg.de/qisserver/rds?state=wplan&act=Raum&pool=Raum&raum.rgid={}'
    url = template.format(roomid)
    return url


def table_from_url(url):
    """
    generates the table from the schedule url
    """
    global t
    with urllib.request.urlopen(url) as response:
       html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    times = {}
    current_time = ''
    segment_of_current_hour = 0
    time_still_running = [0, 0, 0, 0, 0]
    for row in [child for child in list(soup.find('table', {'border': '1'}).children) if child != '\n'][1:]:
        children = (child for child in list(row.children) if child != '\n' and child != None)
        title_label = next(children).find('span')
        segment_of_current_hour += 1
        if title_label:
            segment_of_current_hour = 0
            current_time = title_label.get_text()
            times[current_time] = []
            next(children)
        free_array = []
        for weekday in range(len(time_still_running)):
            if time_still_running[weekday] > 0:
                time_still_running[weekday] -= 1
                free_array.append(False)
            else:
                try:
                    child = next(children)
                    is_lecture = child.get('class')[0] != 'plan1'
                    if is_lecture:
                        time_still_running[weekday] = int(child.get('rowspan')) - 1
                        free_array.append(False)
                    else:
                        free_array.append(True)
                except:
                    free_array.append('error')
        times[current_time].append(free_array)
    try:
        t.update(1)
    except:
        pass
    return times


def room_urls_for_search_url(url):
    """
    the urls of all rooms that are yieled in a search url
    """
    with urllib.request.urlopen(url) as response:
       html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    room_urls = {erg_list_entry.find('a').find('strong').get_text():
                     room_url_for_room_id(erg_list_entry.find('a').get('href').split('.rgid=')[1].split('&')[0])
                 for erg_list_entry in soup.find_all('div', {'class': 'erg_list_entry'})
                 if erg_list_entry.find('div', {'class': 'erg_list_label'}).get_text() == 'Raum:'}
    return room_urls


def raumartids():
    """
    dictionary of format {room_type_name: room_type_id, ...}
    """
    url = 'https://www-sbhome1.zv.uni-wuerzburg.de/qisserver/rds?state=change&type=6&moduleParameter=raumSelectArt&nextdir=change&next=SearchSelect.vm&target=raumSearch&subdir=raum&init=y&source=state%3Dchange%26type%3D5%26moduleParameter%3DraumSearch%26nextdir%3Dchange%26next%3Dsearch.vm%26subdir%3Draum%26_form%3Ddisplay%26topitem%3Dfacilities%26subitem%3Dsearch%26function%3Dnologgedin%26field%3Draumart&raum.gebid=36&targetfield=raumart&_form=display'
    with urllib.request.urlopen(url) as response:
       html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    ids = {room.get_text().lstrip().rstrip(): room.get('href').split('raumartid=')[1].split('&')[0]
           for room in soup.find_all('a', {'class': 'regular'})
           if 'raumartid' in room.get('href')}
    return ids


def buildingids():
    """
    dictionary of format {building_name: building_id, ...}
    """
    url = 'https://www-sbhome1.zv.uni-wuerzburg.de/qisserver/rds?state=change&type=6&moduleParameter=raumSelectGeb&nextdir=change&next=SearchSelect.vm&target=raumSearch&subdir=raum&init=y&source=state%3Dchange%26type%3D5%26moduleParameter%3DraumSearch%26nextdir%3Dchange%26next%3Dsearch.vm%26subdir%3Draum%26_form%3Ddisplay%26topitem%3Dfacilities%26subitem%3Dsearch%26function%3Dnologgedin%26field%3Dgebid&targetfield=gebid&_form=display'
    with urllib.request.urlopen(url) as response:
       html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    ids = {room.get_text().lstrip().rstrip(): room.get('href').split('.gebid=')[1].split('&')[0]
           for room in soup.find_all('a', {'class': 'regular'})
           if 'gebid' in room.get('href')}
    return ids


def room_urls_for_buildings_and_rooms(gebids, raumartids):
    """
    all room urls from a dictionary of building- and room_type ids
    """
    return {k: v for d in [room_urls_for_search_url(search_url_from_id(gebid, raumartid))
         for gebid, raumartid in itertools.product(gebids, raumartids)] for k, v in d.items()}


def room_types_and_buildings(gebids_, raumartids_):
    """
    dictionary of type

    {
        building_name: {
            room_type_name: [
                room_name_1,
                room_name_2
                ],
            room_type_name_2: [
                ...
            ],
            ...
        },
        other_building_name: ...
    }

    with all available rooms in all buildings
    """
    raumartid_list = raumartids()
    buildingid_list = buildingids()

    data = {}

    for gebid, raumartid in itertools.product(gebids_, raumartids_):
        raumart = list(raumartid_list.keys())[list(raumartid_list.values()).index(raumartid)]
        building = list(buildingid_list.keys())[list(buildingid_list.values()).index(gebid)]

        if not building in data:
            data[building] = {}

        url = search_url_from_id(gebid, raumartid)

        with urllib.request.urlopen(url) as response:
           html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        room_names = [erg_list_entry.find('a').find('strong').get_text()
                     for erg_list_entry in soup.find_all('div', {'class': 'erg_list_entry'})
                     if erg_list_entry.find('div', {'class': 'erg_list_label'}).get_text() == 'Raum:']
        data[building][raumart] = room_names
    return data



def entire_plan_from_room_dictionary(d):
    """
    takes a dictionary of type
    {
        room_name: room_url,
        ...
    }
    and returns dictonary of type
    {
        room_name: table
    }
    """
    return {room: table_from_url(d[room]) for room in d}


def sync():
    """
        synchronizes with the server, generates all time tables and saves them to file
    """
    global t
    wanted_room_raumartids = [id for room, id in raumartids().items() if room in ('Hörsaal', 'Seminarraum', 'Praktikumsraum', 'PC-Pool')]
    wanted_building_ids = [id for building, id in buildingids().items() if building in ('Physik', 'Nat.wiss. HS-Bau', 'Informatik', 'Bibl- u Seminarz')]

    import json
    import tqdm
    print('generating room map')
    with open('roommap.json', 'wb') as f:
        f.write(json.dumps(room_types_and_buildings(wanted_building_ids, wanted_room_raumartids), indent = 4, ensure_ascii=False).encode('utf-8'))
    rooms = room_urls_for_buildings_and_rooms(wanted_building_ids, wanted_room_raumartids)
    print('generating time table')
    t = tqdm.tqdm(total=len(rooms))
    plan_by_room = entire_plan_from_room_dictionary(rooms)
    times = {}
    for room in plan_by_room:
        for time in plan_by_room[room]:
            if not time in times:
                times[time] = {}
            times[time][room] = plan_by_room[room][time]
    with open('roomplan.json', 'wb') as f:
        f.write(json.dumps(times, indent = 4, ensure_ascii=False).encode('utf-8'))
    print('done')

sync()
