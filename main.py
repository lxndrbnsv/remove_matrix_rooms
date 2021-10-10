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
            """SELECT room_id FROM rooms WHERE creator = %s;""",
            [CONFIG['bot_id']]
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
            """SELECT token FROM access_tokens WHERE user_id = %s;""",
            [CONFIG["bot_id"]]
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


def login():
    bot_id = CONFIG["bot_id"]
    login_url = f"{CONFIG['matrix_api_url']}/_matrix/client/r0/login"
    data = dict(
        type="m.login.password",
        identifier=dict(
            type="m.id.user",
            user=bot_id
        ),
        password=CONFIG["bot_password"],
        initial_device_display_name="QN API"
    )
    r = requests.post(login_url, json=data)

    return json.loads(r.text)["access_token"]


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
    url = f"{CONFIG['matrix_api_url']}/_synapse/admin/v1/rooms/{room_id}"
    auth_header = {"Authorization": f"Bearer {admin_token}"}
    data = dict(force_purge=True)
    r = requests.delete(url, headers=auth_header, json=data)
    print(
        r, r.text,
        f"\nRoom {room_id} has been deleted!"
    )


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    admin_token = login()
    rooms = get_rooms_list()
    for room in rooms:
        delete_room(room)

