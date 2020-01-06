# PoESniper
Item sniper for Path of Exile

## Requirements
* Python 3.7+ (Make sure you check add to PATH in the installer)

## Instructions
* Run install.bat
* Rename `config.json.dist` to `config.json` and open it
* Change "league" to the league you wish to search in
* Change "POESESSID" to your POE Session id (f12 in browser on pathofexile.com while logged in, application tab, cookies, copy POESESSID)
* Add JSON objects for each item you'd like to snipe
* Run start.bat

> item : Item name
 
> max_price : The highest price you're willing to buy at per singular item

> min_profit : The minimum profit to display (margin * item count)
 
> resale : Price you're flipping at, used to determine profit margin (resale - price)
