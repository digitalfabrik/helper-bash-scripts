#!/usr/bin/env python3 

import requests
import json
import datetime
import configparser
import tempfile
import os
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

config = configparser.ConfigParser()
config.read(os.path.join(os.getenv("HOME"), 'statistics.ini'))
api_key = config['DEFAULT']['api_key']
domain = config['DEFAULT']['domain']

color = {
 'de': 'r-*',
 'en': 'b-*',
 'fr': 'g-*',
}

ax_title = {
 'de': 'Deutsch',
 'en': 'Englisch',
 'fr': 'Französisch'
}

periods = {
 'day': 'Tägliche',
 'month': 'Monatliche'
}

def get_dict(data, period):
 stats = {}
 for lang in data:
  stats[lang] = {}
  stats[lang]['dict'] = {}
  stats[lang]['dates'] = []
  stats[lang]['visitors'] = []
  for date in get_date_list(period):
   key = date.isoformat() if period == "day" else date.strftime("%Y-%m")
   if key in data[lang] and len(data[lang][key]) > 0:
    val = data[lang][key]['nb_actions']
   else:
    val = 0
   stats[lang]['dict'][date] = val
   stats[lang]['dates'].append(date)
   stats[lang]['visitors'].append(val)
 return stats

def get_dates(period):
 today = datetime.date.today()
 first = today.replace(day=1)
 last_month_end = first - datetime.timedelta(days=1)
 last_month_first = last_month_end.replace(day=1)
 if period == 'day':
  return (last_month_first, last_month_end)
 elif period == 'month':
  first_month = (last_month_end - datetime.timedelta(days=364)).replace(day=1)
  return (first_month, last_month_end)

def fetch_data(region, period):
 stats = {}
 dates = get_dates(period)
 date_string = "{},{}".format(dates[0].isoformat(), dates[1].isoformat())
 for lang in config[region]["languages"].split(" "):
  print("Fetching data for (%s, %s)" % (region, lang))
  site_id = str(config[region]["id"])
  url = "https://{}/index.php?date={}&expanded=1&filter_limit=-1&format=JSON&format_metrics=1&idSite={}&method=API.get&module=API&period={}&segment=pageUrl%253D@%25252F{}%25252Fwp-json%25252F&token_auth={}".format(
  domain, date_string, site_id, period, lang, api_key)
  stats[lang] = requests.get(url).json()
 return stats

def plot(region, period, stats):
 print("Plotting ...")
 import matplotlib as mpl
 mpl.use('Agg')
 import matplotlib.pyplot as plt
 plt.cla()
 for lang in stats:
  plt.plot(stats[lang]['dates'], stats[lang]['visitors'], color[lang], label=ax_title[lang], alpha=0.9)
 plt.title("{} Integreat API Aufrufe {}".format(periods[period], region))
 plt.legend(bbox_to_anchor=(0.05, 0.95), loc=2, borderaxespad=0.)
 plt.xticks(rotation=23)
 axes = plt.gca()
 dates = get_dates(period)
 if period == 'day':
  plt.xlabel("Datum")
  axes.set_xlim(dates[0], dates[1])
 else:
  plt.xlabel("Monat")
  axes.set_xlim(dates[0].replace(day=1), dates[1].replace(day=1))
 plt.ylabel("Aufrufe")
 plt.tight_layout()
 global tempdir
 filename = os.path.join(tempdir, '{}-{}.png'.format(region, period))
 plt.savefig(filename, dpi=250)
 plt = None
 return filename

def get_date_list(period):
 if period == 'day':
  dates = get_dates(period)
  days = (dates[1] - dates[0]).days + 2
  day_list = []
  for n in range(1, days):
   day_list.append(dates[0].replace(day=n))
  return day_list
 if period == 'month':
  dates = get_dates(period)
  months_list = []
  for n in range(1, 13):
   months_list.append(dates[0].replace(month=n))
  return months_list

def dump_data(region, period, stats):
 lines = {}
 dates = get_dates(period)
 date_list = get_date_list(period)
 lang_list = list(stats)
 filename = os.path.join(tempdir, '{}-{}.csv'.format(region, period))
 with open(filename, "a") as f:
  f.write("date,{}\n".format(','.join(lang_list)))
  for date in date_list:
   visits = []
   for lang in lang_list:
    visits.append(str(stats[lang]['dict'][date]))
   line = "{},{}\n".format(date.isoformat(), ','.join(visits))
   f.write(line)
 return filename

def generate_mails(region, files):
 text = """Dies ist eine automatisch generierte E-Mail mit den aktuellen
Integreat-Statistiken für Ihre Kommune.

Folgende Daten finden Sie im Anhang:
- Diagram der täglichen Aufrufe im letzten Monat
- Rohdaten der täglichen Aufrufe im letzten Monat
- Diagram de monatlichen Aufrufe im letzten Jahr
- Rohdaten de monatlichen Aufrufe im letzten Jahr

Die Zahlen sind jeweils nach Sprache aufgeschlüsselt.

Bitte antworten sie nicht auf diese E-Mail.

Mit freundlichen Grüßen,
Das Integreat-Team"""
 send_mail("keineantwort@integreat-app.de", [config[region]["email"]], "Integreat Statistiken", text, files, "127.0.0.1")

def send_mail(send_from, send_to, subject, text, files=None, server="127.0.0.1"):
 assert isinstance(send_to, list)
 msg = MIMEMultipart()
 msg['From'] = send_from
 msg['To'] = COMMASPACE.join(send_to)
 msg['Date'] = formatdate(localtime=True)
 msg['Subject'] = subject
 msg.attach(MIMEText(text))
 for f in files or []:
  with open(f, "rb") as fil:
   part = MIMEApplication(
       fil.read(),
       Name=basename(f)
   )
  part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
  msg.attach(part)
 smtp = smtplib.SMTP(server)
 smtp.sendmail(send_from, send_to, msg.as_string())
 smtp.close()

def main():
 global tempdir
 tempdir = tempfile.mkdtemp(prefix="ig-stats_")
 print("Writing to {}".format(tempdir))
 for region in config.sections():
  file_list = []
  for period in config[region]['period'].split(' '):
   stats = get_dict(fetch_data(region, period), period)
   file_list.append(plot(region, period, stats))
   file_list.append(dump_data(region, period, stats))
  generate_mails(region, file_list)

main()
