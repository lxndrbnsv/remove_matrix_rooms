# Removing all rooms for all users on a testing server.

import json
import traceback

import requests
import psycopg2


with open("./settings.json", "r") as json_file:
    CONFIG = json.load(json_file)


def get_rooms_list():
    room_list = []

    connection = psycopg2.connect(
        user=CONFIG["database_user"],
        password=CONFIG["database_password"],
        host=CONFIG["database_host"],
        database=CONFIG["database_name"],
    )

    cursor = connection.cursor()
    try:
        cursor.execute(
            """SELECT room_id FROM rooms WHERE creator = '@ai_bot:m.mybusines.app';""",
            )

        select_data = cursor.fetchall()
        for s in select_data:
            room_list.append(s[0])

    except (Exception, psycopg2.Error) as error:
        traceback.print_exc()
        print(error, flush=True)
    finally:
        if connection:
            cursor.close()
            connection.close()
    print(room_list)
    return room_list


def get_admin_token():
    connection = psycopg2.connect(
        user=CONFIG["database_user"],
        password=CONFIG["database_password"],
        host=CONFIG["database_host"],
        database=CONFIG["database_name"],
    )

    cursor = connection.cursor()
    try:
        cursor.execute(
            """SELECT token FROM access_tokens WHERE user_id = '%s';""",
            CONFIG["bot_id"]
        )

        select_data = cursor.fetchone()

    except (Exception, psycopg2.Error) as error:
        traceback.print_exc()
        print(error, flush=True)
    finally:
        if connection:
            cursor.close()
            connection.close()
    return select_data[0]


def parse_logs():
    r_id = []

    with open("./logs_to_parse.log", "r") as text_file:
        lines = text_file.readlines()

    for l in lines:
        if "'room_id':" in l:
            room_dict = json.loads(l.replace("'", '"'))
            r_id.append(room_dict["room_id"])
            print(l)

    for r in r_id:
        print(r)

    return r_id


def delete_room(room_id):
    url = f"https://matrix.m.qaim.me/_synapse/admin/v1/rooms/{room_id}"
    auth_header = {"Authorization": f"Bearer {get_admin_token()}"}
    data = dict(force_purge=True)
    r = requests.delete(url, headers=auth_header, json=data)
    print(
        r, r.text,
        f"\nRoom {room_id} has been deleted!"
    )


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    rooms = get_rooms_list()
    for room in rooms:
        delete_room(room)

