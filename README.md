# hEV: Horizontal Exit Velocity

Python script that builds yearly hEV leaderboards for batters.

## Requirements

- Python 3.X
- Yearly Statcast data (which you can get using [this script](https://github.com/jefnic23/baseball_savant_scraper))
  - If you already have Statcast data you will need to make sure it's saved with the format `../baseball_savant/data/savant_{year}`, otherwise you'll have to edit the code at line 45 of `hev.py`

## Installation

Download the repo using **Code > Download ZIP**, or clone the repo using git bash.

```bash
git clone https://github.com/jefnic23/wCSW.git
```

## Setup

Open a console inside the `hEV` directory and create a virtual enviroment. 

```bash
python.exe -m venv venv
```

Activate the virtual environment.

```bash
venv\scripts\activate
```

Then install dependencies.

```bash
pip install -r requirements.txt
```

## Usage

Once everything is setup and dependencies are installed, run the script from the console and follow the prompts. 

```bash
python wcsw.py
```

Files are saved to the `data` directory.

Since the script relies on Statcast data, only MLB seasons after 2015 are valid. The script will ask which year you'd like to generate a leaderboard for, so if you want all Statcast seasons you'll have to run the script for each season.