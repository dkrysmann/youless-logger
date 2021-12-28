The python script in this repository extracts the logged data (hour and minute data) from a Youless logger.
The data is stored in a SQLite database named `youless.db` with 2 tables set up:

- `youless_minute` for minute based data
- `youless_hour` for hourly data

# Prerequisite 

In order to run this script you need a Youless logger connected to the same network as the machine you run this script on.
We assume the logger is reachable on `http://youless/` via your browser.

# Setup

You can run this script manually or set up a crontab to run it automatically.
This example sets it up to run every minute:

Edit your crontab

```bash
crontab -e
```

Enter the following line (adjust the path to the script):

```bash
* * * * * /full/path/to/script.py
```

Save it.