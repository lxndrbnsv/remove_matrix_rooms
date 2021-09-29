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
            """SELECT room_id FROM rooms;""",
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
    return room_list


def delete_room(room_id, admin_token):
    url = f"https://test.matrix.mybusines.app/_synapse/admin/v1/rooms/{room_id}"
    auth_header = {"Authorization": f"Bearer {admin_token}"}
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
        delete_room(room, CONFIG["admin_token"])

