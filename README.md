# NOW Test Automation Using Selenium

This repository is an  automation NOW testing using Selenium WebDriver. 

1. [Prerequisites](#Prerequisites)
2. [Running This Project](#Running-This-Project)
3. [Interpreting Results](#Interpreting-Results)
4. [Writing Custom Tests](#Writing-Custom-Tests)
5. [Running At Intervals](#Running-At-Intervals)

## Prerequisites

1. Install [Chrome](https://www.google.com/chrome/)
2. Install [ChromeDriver](https://chromedriver.chromium.org/getting-started)
3. Install [Python3](https://www.python.org/downloads/). 
4. Clone this repository git@github.com:girlCoder8/now-automation.git
```bash
git clone git@github.com:girlCoder8/now-automation.git
```
5. Install the required packages 
```bash
pip install -r requirements.txt
```

## Running This Project

If you are an employee at DIT or if you have the correct credentials to run this project, follow the steps below:

1. Navigate to this repository
2. Create a file called "secret.txt" in this repository. Put the username of a local ServiceNow user on the first line and the password of that user on the second line.
3. Run pytest

```bash
cd /YourPathTo/ServiceNow
echo -e "local_username\nlocal_password" > secret.txt
pytest
```

If you want more verbose output, consider adding the -s flag to pytest which enables all logs to print regardless of whether or not an error was encountered.

```bash
pytest -s
```

If you want to run the tests without opening the Chrome browser (i.e. headless mode), run this command before you run pytest:

```bash
export HEADLESS=true
```

Alternatively, you can disable headless mode by running this command before you run pytest:
```bash
export HEADLESS=false
```

## Writing Custom Tests

To write a custom pytest, perform the following steps:

1. Create a file named test_(your_test_file).py in the Tests folder.
2. Import the following packages in your python file

``` python
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException

import os
import pytest
```

3. Use the following code to create a ServiceNow object

``` python
headless = os.environ["HEADLESS"].lower() == 'true'

options = webdriver.ChromeOptions()
options.add_argument("--disable-popup-blocking")

if headless:
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    
driver = webdriver.Chrome(options=options)
sn = ServiceNow(driver)
```

4. Log in to ServiceNow Using the Side Door or CASS
``` python
# Side Door Login
sn.side_door_login()

#CASS Login
sn.login()
```

5. Write a function for your custom test

``` python
def test_your_test_name():
  # Write your test here
```

6. Run your test by navigating to the ServiceNow directory and running pytest
``` bash
pytest Tests/test_your_test_file.py
```

