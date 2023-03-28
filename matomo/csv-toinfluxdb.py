#!/usr/bin/env python3
"""
Send data from statistics CSV to InfluxDb
"""

import argparse
import csv
import datetime
import requests


def period_string():
    """
    Get string representation of period
    """
    if ARGS.daily:
        return "day"
    return "month"

def log_influxdb(period, key, value, timestamp):
    """
    Log data to InfluxDB & Grafana
    """
    influx_data = "cms-access,period={} {}={} {}".format(
        period, key, value,
        int(datetime.datetime.strptime(timestamp, "%Y-%m-%d").strftime('%s'))*1000*1000)
    requests.post('https://monitoring.tuerantuer.org/write?db=okr',
                  influx_data.encode(),
                  cert=('/etc/pki/client.crt', '/etc/pki/client.key'),
                  verify='/usr/local/share/ca-certificates/ca.crt')

def main():
    """
    iterate over regions and languages
    """
    with open(ARGS.csv, newline='') as csvfile:
        statsreader = csv.DictReader(csvfile, delimiter=',')
        for row in statsreader:
            for key in ["offline-downloads", "total-downloads"]:
                log_influxdb(period_string(), key, row[key], row["date"])

PARSER = argparse.ArgumentParser()
PARSER.add_argument("--csv", help="Path to statistics CSV file")
PARSER.add_argument("--daily", help="Plot daily not monthly intervals.", action='store_true')
ARGS = PARSER.parse_args()

main()
