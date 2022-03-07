# Google_Image_Scraper

![ezgif com-gif-maker](https://user-images.githubusercontent.com/69685614/157089599-e508baad-1fa4-4b5a-b7bc-14bcb385badf.gif)

Google_Image_Scraper is a dynamic Webscraper that scrapes the images behind Google Image search results (so far it's hardcoded for kitten pictures).
It uses SeleniumWebDriver and ChromeDriver to remotely control the Chromium browser. 

ChromeDriver is a standalone server that implements the W3C WebDriver standard: https://chromedriver.chromium.org/

Selenium is an open source suite of tools for automating browser testing: https://www.selenium.dev/

Selenium WebDriver is an open source wrapper for automated driving of many different browsers by providing an API (for example for ChromeDriver): (https://www.selenium.dev/projects/) 

## Deployment

The program is implemented using docker-compose for easy deployability.

Selenium offers docker images for deploying Selenium test suites on Selenium Grid Servers (https://www.selenium.dev/documentation/grid/), which allow the parallelization of browser testing across different machines. I'm using the standalone image for Chromium here as a simple solution. Another docker container consists of the program itself, which accesses the standalone Chroumium container as a "remote" browser.

## Setup (Linux)

1. Installation of docker-compose: https://docs.docker.com/compose/install/

2. Clone the repository into ./Google_Image_Scraper: `git clone https://github.com/FabianGruben/Google_Image_Scraper/`

3. Start up the docker-compose pipeline in the background (after changing directory): `docker-compose up -d`

4. Access the program container using bash: `docker exec -ti google_scraper /bin/bash`

5. Start the script and download a lot of kitten pictures from Google Image Search: `python3 selenium_scraper.py`

## Features / Learnings

- Logger
- Programmed using some OOP principles (Factory Pattern, Composition)
- Exception Handling for dealing with errors that are common in interacting with Websites and useful for signaling within the control flow
- Created some custom exception classes for dealing with webscraping problems
- Created some custom expected conditions for Selenium Webdriver

## Next Steps

- Allowing arguments from the command line for number of images and search terms
- Refactoring
- Implement tests for download success

