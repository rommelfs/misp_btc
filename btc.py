#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymisp import PyMISP
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
try:
    conversion_rates = json.load(open("text_dump.txt"))
except:
    conversion_rates = {}

def get_consumption(output=False):
    req = requests.get(converter_rls)
    jreq = req.json()
    minute = str(jreq['Minute']['CallsLeft']['Histo'])
    hour   = str(jreq['Hour']['CallsLeft']['Histo'])
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
        # If not cached, we have to get the converion rates
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
                #print(minute)
                #get_consumption(output=True)
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
            # Since we have the rates, store them in the cache
            conversion_rates[date] = (usd, eur)
        except Exception as ex:
            print(ex)
            get_consumption(output=True)
    # Actually convert and return the values
    u = usd * btc
    e = eur * btc
    return u,e


def init(url, key):
    return PyMISP(misp_url, misp_key, misp_verifycert, 'json')


m = init(misp_url, misp_key)

try:
    if sys.argv[1] == "-h":
        print("Usage: %s [time]" % sys.argv[0])
        print("       where [time] can be a statement recognized by MISP, e.g. 1d, 1h")
        sys.exit(1)
    else:
        timerange = sys.argv[1]
except:
    timerange = "1d"

response = m.search(controller='attributes', type_attribute="btc", last=str(timerange))
for r in response['response']['Attribute']:
    btc = r['value']
    print("\nAddress:\t" + btc)
    try:
        req = requests.get(blockchain_all+btc+"?limit=50&filter=5")
        jreq = req.json()
    except Exception as e:
        #print(e)
        print(req.text)
        continue

    n_tx = jreq['n_tx']
    balance = float(jreq['final_balance'] / 100000000)
    rcvd = float(jreq['total_received'] / 100000000)
    sent = float(jreq['total_sent'] / 100000000)
    output = 'Balance:\t{0:.10f} BTC (+{1:.10f} BTC / -{2:.10f} BTC)'
    print(output.format(balance, rcvd, sent))
    print("Transactions:\t" + str(n_tx))
    if n_tx > 0:
        print("======================================================================================")
    i = 0
    while i < n_tx:
        req = requests.get(blockchain_all+btc+"?limit=50&offset="+str(i)+"&filter=5")
        jreq = req.json()
        if jreq['txs']:
            for transactions in jreq['txs']:
                sum = 0
                sum_counter = 0
                for tx in transactions['inputs']:
                    script_old = tx['script']
                    if tx['prev_out']['value'] != 0 and tx['prev_out']['addr'] == btc:
                        datetime = time.strftime("%d %b %Y %H:%M:%S %Z", time.localtime(int(transactions['time'])))
                        value = float(tx['prev_out']['value'] / 100000000 )
                        u,e = convert(value, transactions['time'])
                        print("#" + str(n_tx - i) + "\t" + str(datetime) + "\t-{0:10.8f} BTC {1:10.2f} USD\t{2:10.2f} EUR".format(value, u, e).rstrip('0'))
                        if script_old != tx['script']:
                            i += 1
                        else:
                            sum_counter += 1
                            sum += value
                if sum_counter > 1:
                    u,e = convert(sum, transactions['time'])
                    print("\t\t\t\t\t----------------------------------------------")
                    print("#" + str(n_tx - i) + "\t\t\t\t  Sum:\t-{0:10.8f} BTC {1:10.2f} USD\t{2:10.2f} EUR\n".format(sum, u, e).rstrip('0'))
                for tx in transactions['out']:
                    if tx['value'] != 0 and tx['addr'] == btc:
                        datetime = time.strftime("%d %b %Y %H:%M:%S %Z", time.localtime(int(transactions['time'])))
                        value = float(tx['value'] / 100000000 )
                        u,e = convert(value, transactions['time'])
                        print("#" + str(n_tx - i) + "\t" + str(datetime) + "\t {0:10.8f} BTC {1:10.2f} USD\t{2:10.2f} EUR".format(value, u, e).rstrip('0'))
                        #i += 1
                i += 1

json.dump(conversion_rates, open("text_dump.txt",'w'))
