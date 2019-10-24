# PoESniper
 CLI-Based Item sniper for Path of Exile

## Requirements
* Python 3.6+
* Cmder (https://cmder.net/)

## Installing required libraries
* `python -m pip install --upgrade pip`
* `python -m pip install selenium bs4 apscheduler`

## Instructions
* Rename `config.dist.json` to `config.json` and open it
* Add JSON objects for each item you'd like to snipe
> identifier : Unique identifier at the end of your trade URL (https://www.pathofexile.com/trade/exchange/Blight/IDENTIFIER)
 
> max_price : The highest price you're willing to buy at per singular item

> min_profit : The minimum profit to display (margin * item count)
 
> resale : Price you're flipping at, used to determine profit margin (resale - price)
 
> interval : Interval at which to refresh the page to scan for new results (default: 15)

* Start cmder
* Copy/paste the directory of PoESniper and do `cd "<directory here>"`
* run `python PoESniper.py`
* Type `commands` and press enter to view available commands
