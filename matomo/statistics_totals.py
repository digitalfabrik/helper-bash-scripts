#!/usr/bin/env python3
"""
Plot summary statistics for integreat.app
"""

import argparse
import csv
import datetime
import os
import requests

from dateutil.rrule import rrule, MONTHLY, DAILY

COLOR = {
    'offline-downloads': '#000000',
    'de': '#7e1e9c',
    'en': '#15b01a',
    'fr': '#0343df',
    'ar': '#ff81c0',
    'fa': '#653700',
    'am': '#e50000',
    'ru': '#00ffff',
    'tr': '#029386',
    'ro': '#f97306',
    'ku': '#96f97b',
    'ti': '#c20078',
    'sr': '#ffff14',
    'per': '#75bbfd',
    'bg': '#929591',
    'so': '#89fe05',
    'pl': '#bf77f6',
    'es': '#9a0eea',
    'de-si': '#033500',
    'hr': '#06c2ac',
    'it': '#c79fef',
    'hu': '#00035b',
    'el': '#d1b26f',
    'ps': '#00ffff',
    'kmr': '#13eac9',
    'sr-Latn': '#06470c',
    'sr-latn': '#06470c',
    'ur': '#ae7181',
    'ka': '#35063e',
    'ckb': '#01ff07',
    'mk': '#650021',
    'zh-CN': '#6e750e',
    'prs': '#e6daa6',
    'sq': '#0504aa',
    'uk': '#001146'
}

AX_TITLE = {
    'offline-downloads': 'Offline Downloads',
    'de': 'Deutsch',
    'en': 'Englisch',
    'es': 'Spanisch',
    'fr': 'Französisch',
    'ar': 'Arabisch',
    'fa': 'Farsi',
    'am': 'Amharisch',
    'ru': 'Russisch',
    'tr': 'Türkisch',
    'ro': 'Rumänisch',
    'ku': 'Kurdisch',
    'ti': 'Tigrinya',
    'sr': 'Serbisch',
    'per': 'Persisch',
    'bg': 'Bulgarisch',
    'so': 'Somali',
    'pl': 'Polnisch',
    'de-si': 'Einfaches Deutsch',
    'hr': 'Kroatisch',
    'it': 'Italienisch',
    'hu': 'Ungarisch',
    'el': 'Griechisch',
    'ps': 'Paschto',
    'kmr': 'Kurmandschi',
    'sr-Latn': 'Serbisch (Latein)',
    'sr-latn': 'Serbisch (Latein)',
    'ur': 'Urdu',
    'ka': 'Georgisch',
    'ckb': 'Sorani',
    'mk': 'Mazedonisch',
    'zh-CN': 'Chinesisch',
    'prs': 'Dari',
    'sq': 'Albanisch',
    'uk': 'Ukraininisch'
}

PERIODS_ADJ = {
    'day': 'Tägliche',
    'month': 'Monatliche'
}

PERIODS_DEU = {
    'day': 'Monat',
    'month': 'Jahr'
}


def get_dict(data):
    """
    transform matomo data to dict
    """
    stats = {}
    for lang in data:
        stats[lang] = {}
        stats[lang]['dict'] = {}
        stats[lang]['dates'] = []
        stats[lang]['visitors'] = []
        for date in get_date_list():
            key = date.strftime('%Y-%m-%d') if ARGS.daily else date.strftime("%Y-%m")
            if key in data[lang] and data[lang][key] and 'nb_actions' in data[lang][key]:
                val = data[lang][key]['nb_actions']
            else:
                val = 0
            stats[lang]['dict'][date] = val
            stats[lang]['dates'].append(date)
            stats[lang]['visitors'].append(val)
    return stats


def get_dates():
    """
    get start and end dates of period
    """
    if ARGS.month:
        today = datetime.datetime.strptime(ARGS.month, "%Y-%m")
    else:
        today = datetime.date.today()
    first = today.replace(day=1)
    last_month_end = first - datetime.timedelta(days=1)
    last_month_first = last_month_end.replace(day=1)
    if ARGS.daily:
        return (last_month_first, last_month_end)
    first_month = (last_month_end - datetime.timedelta(days=364)).replace(day=1)
    return (first_month, last_month_end)


def fetch_data(region, regions, dates):
    """
    Get data from Matomo
    """
    stats = {}
    date_string = "{},{}".format(dates[0].strftime('%Y-%m-%d'), dates[1].strftime('%Y-%m-%d'))
    for lang in regions[region]["languages"]:
        if ARGS.verbose:
            print("Fetching data for (%s, %s)" % (regions[region]["name"], lang))
        url = ("https://{}/index.php?date={}&expanded=1&filter_limit=-1&"
               "format=JSON&format_metrics=1&idSite={}&method=API.get&module=API&"
               "period={}&segment=pageUrl%253D@%25252F{}%25252Fwp-json%25252F&"
               "token_auth={}").format(
                   ARGS.matomo_url, date_string, regions[region]["site_id"],
                   period_string(), lang, ARGS.matomo_token)
        if ARGS.verbose:
            print(url)
        stats[lang] = requests.get(url).json()

    url = ("https://{}/index.php?date={}&expanded=1&filter_limit=-1&format=JSON&"
           "format_metrics=1&idSite={}&method=API.get&module=API&period={}&"
           "segment=pageUrl=@%252Fpages&token_auth={}").format(
               ARGS.matomo_url, date_string, regions[region]["site_id"],
               period_string(), ARGS.matomo_token)
    if ARGS.verbose:
        print(url)
    stats["offline-downloads"] = requests.get(url).json()
    return stats


def plot(region, stats, month, tempdir):
    """
    Plot graph
    """
    if ARGS.verbose:
        print("Plotting ...")
    import matplotlib as mpl
    import matplotlib.dates as mdates
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    plt.cla()
    for lang in stats:
        plt.plot(stats[lang]['dates'], stats[lang]['visitors'],
                 marker='*', linestyle='-', markerfaceCOLOR=COLOR[lang],
                 markeredgeCOLOR=COLOR[lang], COLOR=COLOR[lang],
                 label=AX_TITLE[lang], alpha=0.9)
    plt.title("{} Integreat API Aufrufe {} {}".format(PERIODS_ADJ[period_string()], region, month))
    plt.legend(bbox_to_anchor=(0.05, 0.95), loc=2, borderaxespad=0.)
    plt.xticks(rotation=23)
    axes = plt.gca()
    dates = get_dates()
    if ARGS.daily:
        plt.xlabel("Datum")
        axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        axes.set_xlim(dates[0], dates[1])
    else:
        plt.xlabel("Monat")
        axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        axes.set_xlim(dates[0].replace(day=1), dates[1].replace(day=1))
    plt.ylabel("Aufrufe")
    plt.tight_layout()
    filename = os.path.join(tempdir, '{}_{}_{}.png'.format(
        region, month, PERIODS_DEU[period_string()]))
    plt.savefig(filename, dpi=250)
    plt = None
    return filename


def get_date_list():
    """
    Generate list of dates between start and end dates
    """
    if ARGS.daily:
        dates = get_dates()
        day_list = [dt for dt in rrule(DAILY, dtstart=dates[0], until=dates[1])]
        return day_list
    dates = get_dates()
    months_list = [dt for dt in rrule(MONTHLY, dtstart=dates[0], until=dates[1])]
    return months_list


def dump_data(region, stats, month, tempdir):
    """
    Write data to CSV file
    """
    date_list = get_date_list()
    filename = os.path.join(tempdir, '{}_{}_{}.csv'.format(
        region, month,
        PERIODS_DEU[period_string()]))
    with open(filename, "w") as csv_file:
        csv_file.write("date,{}\n".format(','.join(stats)))
        for date in date_list:
            visits = []
            for lang in stats:
                visits.append(str(stats[lang]['dict'][date]))
            line = "{},{}\n".format(date.strftime('%Y-%m-%d'), ','.join(visits))
            csv_file.write(line)
    return filename


def period_string():
    """
    Get string representation of period
    """
    if ARGS.daily:
        return "day"
    return "month"

def sum_stats(total_stats, stats):
    """
    Add stats of single region to sum of all regions
    """
    for lang in stats:
        if lang in total_stats:
            for key in stats[lang]["dict"]:
                val = stats[lang]["dict"][key]
                if key in total_stats[lang]["dict"]:
                    total_stats[lang]["dict"][key] += val
                else:
                    total_stats[lang]["dict"][key] = val
        else:
            total_stats[lang] = stats[lang]
    return total_stats

def read_regions_csv(csv_path):
    """
    Read CSV file with region information with format:
    name, matomo_id, languages
    """
    regions = {}
    with open(csv_path, newline='\n') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csv_reader:
            if row[0] == "slug":
                continue
            regions[row[0]] = {
                "name": row[1],
                "site_id": row[2],
                "languages": row[3].split(" ")
            }
    return regions

def main():
    """
    iterate over regions and languages
    """
    if ARGS.region:
        selected_regions = [i.strip() for i in ARGS.region.split(",")]
    regions = read_regions_csv(ARGS.csv_path)
    total_stats = {}
    for region in regions:
        if ARGS.region and region not in selected_regions:
            continue
        file_list = []
        dates = get_dates()
        month = dates[1].strftime('%Y-%m')
        tempdir = "/tmp/integreat-stats-{}".format(month)
        try:
            os.mkdir(tempdir)
        except FileExistsError:
            pass
        stats = get_dict(fetch_data(region, regions, dates))
        total_stats = sum_stats(total_stats, stats)
    file_list.append(plot("total", total_stats, month, tempdir))
    file_list.append(dump_data("total", total_stats, month, tempdir))
    os.chmod("/var/www/statistics/{}".format(month), 0o755)


PARSER = argparse.ArgumentParser()
PARSER.add_argument("--verbose", help="increase output verbosity", action='store_true')
PARSER.add_argument("--region",
                    help="Comma separated list of regions to send statistics to. Use quotes.")
PARSER.add_argument("--month", help="A month for which to send the data. Format: YYYY-MM")
PARSER.add_argument("--csv-path", help="Path to regions CSV file")
PARSER.add_argument("--matomo-url", help="URL to Matomo")
PARSER.add_argument("--matomo-token", help="Matomo API Token")
PARSER.add_argument("--daily", help="Plot daily not monthly intervals.")
ARGS = PARSER.parse_args()

main()
