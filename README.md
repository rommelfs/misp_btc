# misp_btc
get BTC addresses from MISP and fetch BTC transactions 

# Description
Use PyMISP to connect to MISP and fetch a list of BTC addresses in a given time range.
Get the balance and all transactions recorded in Blockchain for the address.
Shows the conversion rate in EUR and USD for the transaction at the date of transaction.

# Example
```
Address:    1QHEbZG8NQT6vYCC8pyHvteNcmJ78B3ak3
Balance:    0.0000054700 BTC (+1.3289177500 BTC / -1.3289122800 BTC)
Transactions:   16
======================================================================================
#16 19 Nov 2018 21:32:27 CET    -0.00089649 BTC       4.31 USD        3.70 EUR
#16 19 Nov 2018 21:32:27 CET    -0.13507322 BTC     649.65 USD      557.18 EUR
                    ----------------------------------------------
#16               Sum:  -0.13596971 BTC     653.96 USD      560.88 EUR

#15 16 Nov 2018 13:21:10 CET     0.13507322 BTC     754.56 USD      655.10 EUR
#14 15 Nov 2018 21:49:48 CET     0.00089649 BTC       5.06 USD        4.43 EUR
#13 15 Nov 2018 14:13:57 CET    -0.12400000 BTC     700.29 USD      613.05 EUR
#13 15 Nov 2018 14:13:57 CET    -0.12624600 BTC     712.97 USD      624.15 EUR
#13 15 Nov 2018 14:13:57 CET    -0.11388781 BTC     643.18 USD      563.06 EUR
                    ----------------------------------------------
#13               Sum:  -0.36413381 BTC    2056.45 USD     1800.26 EUR

#12 14 Nov 2018 17:08:14 CET     0.11388781 BTC     653.88 USD      573.12 EUR
#11 14 Nov 2018 09:03:30 CET     0.12400000 BTC     711.94 USD      624.01 EUR
#10 13 Nov 2018 22:53:13 CET     0.12624600 BTC     800.29 USD      705.22 EUR
#9  12 Nov 2018 09:07:23 CET    -0.07500000 BTC     478.46 USD      421.02 EUR
#9  12 Nov 2018 09:07:23 CET    -0.13330000 BTC     850.38 USD      748.29 EUR
#9  12 Nov 2018 09:07:23 CET    -0.11513406 BTC     734.49 USD      646.32 EUR
#9  12 Nov 2018 09:07:23 CET    -0.11430680 BTC     729.22 USD      641.67 EUR
#9  12 Nov 2018 09:07:23 CET    -0.12320000 BTC     785.95 USD      691.60 EUR
#9  12 Nov 2018 09:07:23 CET    -0.14713100 BTC     938.62 USD      825.93 EUR
#9  12 Nov 2018 09:07:23 CET    -0.12073690 BTC     770.24 USD      677.77 EUR
                    ----------------------------------------------
#9                Sum:  -0.82880876 BTC    5287.35 USD     4652.60 EUR

#8  10 Nov 2018 18:57:32 CET     0.00000547 BTC       0.03 USD        0.03 EUR
#7  09 Nov 2018 15:18:27 CET     0.07500000 BTC     478.35 USD      421.04 EUR
#6  09 Nov 2018 03:27:16 CET     0.11430680 BTC     729.05 USD      641.70 EUR
#5  08 Nov 2018 23:58:24 CET     0.13330000 BTC     859.26 USD      754.14 EUR
#4  08 Nov 2018 18:55:06 CET     0.14713100 BTC     948.42 USD      832.39 EUR
#3  07 Nov 2018 22:41:58 CET     0.12073690 BTC     788.37 USD      688.59 EUR
#2  07 Nov 2018 17:31:35 CET     0.11513406 BTC     751.79 USD      656.63 EUR
#1  07 Nov 2018 12:57:04 CET     0.12320000 BTC     804.46 USD      702.63 EUR

======================================================================================
Total received: 1.32891775 BTC    8285.46 USD      7259.03 EUR
Total spent:    1.32891228 BTC    7997.76 USD      7013.74 EUR
```

# Usage
```
# misp_btc$ python3.4 btc.py -h
Usage: btc.py [<TIME> | -b <BTC address> | -e <EVENTID> | -a <TIMEFRAME> | -a <TIMEFRAME_FROM> <TIMEFRAME_TO>]
       where <TIME>, <TIMEFRAME>, <TIMEFRAME_FROM>, <TIMEFRAME_TO> can be a statement recognized by MISP, e.g. 1d, 1h
       Just giving <TIME> by default shows all attributes of events published since <TIME>
       Specifying -a is an attribute search and the time specified is related to the attribute modification/creation
     or
       -a <TIMEFRAME>
     or
       -a <TIMEFRAME_FROM> <TIMEFRAME_TO>
     or
       -b <BTC address> where <BTC address> is a valid BTC address
     or
       -e <EVENTID> where <EVENTID> is a valid MISP event ID
```

# Requirements

```
pymisp 
argparse
os
sys
json
requests
time
datetime
```

A `keys.py` configuration file is required that holds valid MISP credentials

For caching reasons, it is expected to write (and read) a file `conversion_rates_dump.txt` in the current directory.

# External requirements

API lookups are being performed agains:
```
blockchain.info
cryptocompare.com
```

# Integration with MISP
In https://github.com/MISP/misp-modules#expansion-modules is a module version of this tool that integrates the search into MISP


# Copyright

Copyright: Sascha Rommelfangen, CIRCL, Smile g.i.e, 2018-11-12


# License

GNU General Public License v2.0

Reminder of the Warranty clause of the GPLv2: BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.


