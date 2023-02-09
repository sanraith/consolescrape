# consolescrape

Python app to scrape a webshop for Nintendo Switch games,
and save the historical price and availability data into a database.

Python version: 3.8+

## Setup

    git clone https://github.com/sanraith/consolescrape
    cd consolescrape
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r .\requirements.txt

    # If the lxml/libxml install fails:
    - Download the pre-built version from here: https://pypi.org/project/lxml/#files
    - pip install .\lxml-4.9.2-cp311-cp311-win_amd64.whl
    - pip install -r .\requirements.txt

    deactivate

## Run

    .\run.bat
