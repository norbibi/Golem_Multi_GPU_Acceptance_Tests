import argparse
import csv
import json
from time import mktime, strptime

from bottle import route, run
from bottle.ext.websocket import GeventWebSocketServer


@route("/")
def events():
    result = {}
    try:
        with open(events_file_path, "r") as file_with_events:
            reader = csv.DictReader(file_with_events, fieldnames=["event", "timestamp"])
            for row in reader:
                try:
                    result[row["event"]] = mktime(strptime(row["timestamp"], "%a %b %d %H:%M:%S %Z %Y"))
                except ValueError:
                    continue
    except FileNotFoundError:
        pass

    return json.dumps(result)


def get_args():
    parser = argparse.ArgumentParser(description="Maintenance server")
    parser.add_argument(
        "-f",
        "--events_file",
        type=str,
        required=True,
        help="Absolute path to file with events.",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        required=True,
        help="Port on which maintenance server will be run.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    events_file_path = args.events_file
    run(host="0.0.0.0", port=args.port, server=GeventWebSocketServer)