### SimpleRankings

A simple ranking engine and website in python

-

#### Setup

Install `python 2.7` and `flask`.

```pip install flask```

-

#### Run

```
python __init__.py -n "Name of your league -s "Your sport"
```

#### In use

To edit configuration, run once then close. There will be a file called `config.txt` which can be edited.

```
[ui]
league_title = # The name of the league
sport = # The sport that the league is used for
host = 0.0.0.0 # What interface to attach to for the website. 0.0.0.0 is all interface
port = 180 # What port to use for the website
show_rating = 1 # Show rating in the ratings table
show_normalised_rating = 0 # Show normalised_rating in the ratings table (many player games worth the same as 2 player games
sort_by_normalised = 0 # Sort by normalised_rating rather than standard rating

[rankings]
initial_k = 30  # The initial multiplier for ratings. Set high to bias towards early games (to get players established quickly)
standard_k = 16 # The standard multiplier for ratings. How much is each game worth.
```
