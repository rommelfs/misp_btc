#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymisp import PyMISP, MISPEvent, MISPObject
from keys import misp_url, misp_key,misp_verifycert
import argparse
import os
import sys
import json
import requests
import time
import datetime
blockchain_firstseen='https://blockchain.info/q/addressfirstseen/'
blockchain_balance='https://blockchain.info/q/addressbalance/'
blockchain_totalreceived='https://blockchain.info/q/getreceivedbyaddress/'
blockchain_all='https://blockchain.info/rawaddr/'
converter = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym=BTC&tsyms=USD,EUR&ts='
converter_rls = 'https://min-api.cryptocompare.com/stats/rate/limit'
g_rate_limit = 300
start_time = time.time()
now = time.time()
s_in = {'BTC': 0, 'EUR': 0, 'USD': 0}
s_out = {'BTC': 0, 'EUR': 0, 'USD': 0}
n_tx = 0
i = 0
btc = None
jreq = None

try:
    conversion_rates = json.load(open("conversion_rates_dump.txt"))
except:
    conversion_rates = {}

def get_consumption(output=False):
    global jreq
    try:
        req = requests.get(converter_rls)
        jreq = req.json()
        minute = str(jreq['Data']['calls_left']['minute'])
        hour   = str(jreq['Data']['calls_left']['hour'])
    except:
        minute = str(-1)
        hour = str(-1)
    if output is True:
        print("Calls left this minute / hour: " + minute + " / " + hour)
    return minute, hour


def convert(btc, timestamp):
    global g_rate_limit
    global start_time
    global now
    global conversion_rates
    date = time.strftime('%Y-%m-%d', time.localtime(timestamp))
    # Lookup conversion rates in the cache:
    if date in conversion_rates:
        (usd, eur) = conversion_rates[date]
    else:
        # If not cached, we have to get the conversion rates
        # We have to be careful with rate limiting on the server side
        if g_rate_limit == 300:
            minute, hour = get_consumption()
        g_rate_limit -= 1
        now = time.time()
        delta = now - start_time
        #print(g_rate_limit)
        if g_rate_limit <= 10:
            minute, hour = get_consumption(output=True)
            if int(minute) <= 10:
                time.sleep(3)
            else:
                print(minute)
                start_time = time.time()
                g_rate_limit = int(minute)
        try:
            req = requests.get(converter+str(timestamp))
            jreq = req.json()
            usd = jreq['BTC']['USD']
            eur = jreq['BTC']['EUR']
            # Since we have the rates, add them to the cache
            conversion_rates[date] = (usd, eur)
        except Exception as ex:
            print(ex)
            get_consumption(output=True)
    # Actually convert and return the values
    u = usd * btc
    e = eur * btc
    return u,e

def print_result(btc, epoch, positive):
    datetime = time.strftime("%d %b %Y %H:%M:%S %Z", time.localtime(int(epoch)))
    value = float(btc / 100000000 )
    u,e = convert(value, epoch)
    if positive:
        print("#" + str(n_tx - i) + "\t" + str(datetime) + "\t {0:10.8f} BTC {1:10.2f} USD\t{2:10.2f} EUR".format(value, u, e).rstrip('0'))
        s_in['BTC'] += value
        s_in['EUR'] += e
        s_in['USD'] += u
    else:
        print("#" + str(n_tx - i) + "\t" + str(datetime) + "\t{0:10.8f} BTC {1:10.2f} USD\t{2:10.2f} EUR".format(-value, -u, -e).rstrip('0'))
        s_out['BTC'] += value
        s_out['EUR'] += e
        s_out['USD'] += u

def init(url, key):
    return PyMISP(misp_url, misp_key, misp_verifycert, 'json', debug=False)

def decorate(style=1):
    # full line
    if style is 1:
        print("-"*86)
    # half line, right aligned
    if style is 2:
        print("\t\t\t\t\t" + "-"*46)

def work_on(btc):
    global n_tx
    global i
    global jreq
    decorate()
    print("Address:\t" + btc)
    try:
        req = requests.get(blockchain_all+btc+"?limit=50&filter=5")
        jreq = req.json()
    except Exception as e:
        print(req.text)
        return

    n_tx = jreq['n_tx']
    balance = float(jreq['final_balance'] / 100000000)
    rcvd = float(jreq['total_received'] / 100000000)
    sent = float(jreq['total_sent'] / 100000000)
    output = 'Balance:\t{0:.10f} BTC (+{1:.10f} BTC / -{2:.10f} BTC)'
    print(output.format(balance, rcvd, sent))
    print("Transactions:\t" + str(n_tx))
    if n_tx > 0:
        decorate()
    i = 0
    while i < n_tx:
        try:
            req = requests.get(blockchain_all+btc+"?limit=50&offset="+str(i)+"&filter=5")
        except Exception as e:
            print(e)
            time.sleep(3)
            try:
                req = requests.get(blockchain_all+btc+"?limit=50&offset="+str(i)+"&filter=5")
            except:
                sys.exit(1)
        jreq = req.json()
        if jreq['txs']:
            for transactions in jreq['txs']:
                sum = 0
                sum_counter = 0
                for tx in transactions['inputs']:
                    script_old = tx['script']
                    try:
                        addr_in = tx['prev_out']['addr']
                    except KeyError:
                        addr_in = None

                    try:
                        prev_out = tx['prev_out']['value']
                    except KeyError:
                        prev_out = None
                    if prev_out is not None and prev_out != 0 and addr_in == btc:
                        value = prev_out
                        print_result(value, transactions['time'], positive=False)
                        if script_old != tx['script']:
                            i += 1
                        else:
                            sum_counter += 1
                            sum += (value / 100000000)
                if sum_counter > 1:
                    u,e = convert(sum, transactions['time'])
                    decorate(style=2)
                    print("#" + str(n_tx - i) + "\t\t\t\t  Sum:\t{0:10.8f} BTC {1:10.2f} USD\t{2:10.2f} EUR\n".format(-sum, -u, -e).rstrip('0'))
                for tx in transactions['out']:
                    try:
                        addr_out = tx['addr']
                    except KeyError:
                        addr_out = None
                    if tx['value'] != 0 and addr_out == btc:
                        print_result(tx['value'], transactions['time'], positive=True)
                i += 1


m = init(misp_url, misp_key)

try:
    if sys.argv[1] == "-a":
        if len(sys.argv) < 3:
            print("Using -a requires to specify a timeframe")
            sys.exit(0)
        else:
            timestamp = sys.argv[2]
        if len(sys.argv) == 4:
            timestamp = [timestamp, sys.argv[3]]
        response = m.search(controller='attributes', type_attribute="btc", timestamp=timestamp)
    elif sys.argv[1] == "-b":
        if len(sys.argv) < 3:
            print("Using -b requires to specify a BTC address")
            sys.exit(0)
        else:
             btc = sys.argv[2]
    elif sys.argv[1] == "-e":
        if len(sys.argv) < 3:
            print("Using -e requires to specify a MISP event ID")
            sys.exit(0)
        else:
            eventid = sys.argv[2]
            response = m.search(controller='attributes', type_attribute="btc", eventid=eventid)
    elif sys.argv[1] == "-h":
        print("Usage: %s [<TIME> | -b <BTC address> | -e <EVENTID> | -a <TIMEFRAME> | -a <TIMEFRAME_FROM> <TIMEFRAME_TO>]" % sys.argv[0])
        print("       where <TIME>, <TIMEFRAME>, <TIMEFRAME_FROM>, <TIMEFRAME_TO> can be a statement recognized by MISP, e.g. 1d, 1h")
        print("       Just giving <TIME> by default shows all attributes of events published since <TIME>")
        print("       Specifying -a is an attribute search and the time specified is related to the attribute modification/creation")
        print("     or")
        print("       -a <TIMEFRAME>")
        print("     or")
        print("       -a <TIMEFRAME_FROM> <TIMEFRAME_TO>")
        print("     or")
        print("       -b <BTC address> where <BTC address> is a valid BTC address")
        print("     or")
        print("       -e <EVENTID> where <EVENTID> is a valid MISP event ID")
        sys.exit(0)
    else:
        timerange = sys.argv[1]
except SystemExit:
    sys.exit(0)
except Exception as e:
    print(e)
    timerange = "1d"
    print("Defaulting to all attributes of events published during the last day")

try: timerange
except NameError: timerange = None

if timerange is not None:
    response = m.search(controller='attributes', type_attribute="btc", last=str(timerange))

if btc is not None:
    work_on(btc)
else:
    for r in response['response']['Attribute']:
        btc = r['value']
        work_on(btc)

# If we have a total sum, print it
if s_in['BTC'] > 0 or s_out['BTC'] > 0:
    decorate()
    print("\t\t\tTotal received:\t {0:10.8f} BTC {1:10.2f} USD\t{2:10.2f} EUR".format(s_in['BTC'], s_in['USD'], s_in['EUR']).rstrip('2'))
    print("\t\t\tTotal spent:\t {0:10.8f} BTC {1:10.2f} USD\t{2:10.2f} EUR".format(s_out['BTC'], s_out['USD'], s_out['EUR']).rstrip('0'))
    decorate()

# Save the cache into a file
with open('conversion_rates_dump.txt', 'w') as f:
    json.dump(conversion_rates, f, ensure_ascii=False)


