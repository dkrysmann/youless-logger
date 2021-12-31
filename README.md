This repository contains 2 applications:
1. A script to extract data from the a youless logger
2. A dash-application which creates a dashboard to visualize the data

# Prerequisite 
In order to run this script and the app you need a Youless logger connected to the same network as the machine you run this script on.
We assume the logger is reachable on `http://youless/` via your browser.

# Logger
The python script `looger.py` in this repository extracts the logged data (hour and minute data) from a Youless logger.
The data is stored in a SQLite database named `youless.db` with 2 tables set up:

- `youless_minute` for minute based data
- `youless_hour` for hourly data

# Dashboard
To be done

# Setup

## Script

You can run the logger script (`logger.py`)manually or set up a crontab to run it automatically.
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