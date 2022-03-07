#%%" ai
from time import sleep


import requests
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


from custom_exceptions.exceptions import TimeoutExceptionShowMoreImagesButton
from custom_exceptions.exceptions import\
    NoSuchElementExceptionShowMoreImagesButton
from custom_exceptions.exceptions import NotEnoughResultsError
from custom_exceptions.exceptions import FileTypeNotImage
from custom_exceptions.exceptions import KeyErrorNoContentTypeHTTPError
from custom_exceptions.exceptions import ScrollNotWorkingError
from custom_expected_conditions import custom_expected_conditions

from logger import setup_custom_logger

logger = setup_custom_logger("GOOGLE IMAGE SCRAPER")
if (logger.hasHandlers()):
    logger.handlers.clear()

logger = setup_custom_logger("GOOGLE IMAGE SCRAPER")


# To Do: 1. cleaner better exception handling
# 2. Make it a python package and make a nicer github page for it
# 4. logger instead of print


class GoogleImageScraper():
    """
    Initialize and control the instances of the class ImageQuery, which
    download the files for the different search terms.

    For some reason Selenium does not work if the WebDriver is
    re-initialized in the same class for repeated search queries:
    Selenium only works for repeated search queries if the WebDriver is
    re-initialized in a new class (=ImageQuery) every time.

    Instance variables:
        -search_url: String of search URL of Google Image Search Query
        with q="searchstring" replaced by q={q}
        -search_term_list: List of search terms
        -DRIVER_PATH: path to chromedriver
        -number_files_wanted: Number of files to download for each search
        term
        -results: Empty dictionary that is filled with with keys equal
        to search terms and values containing a list of tuples of links
        and relative file paths on harddrive for successfully downloaded
        images
    Methods:
        -.download_images(): Initialize instances of ImageQuery and
        use them to download images for search terms
    """

    def __init__(
        self,
        search_url,
        search_term_list,
        DRIVER_PATH,
        number_files_wanted,
        chrome_options):

        self.search_url = search_url
        self.driver_path = DRIVER_PATH
        self.search_term_list = search_term_list
        self.number_files_wanted = number_files_wanted
        self.chrome_options = chrome_options
        self.results = {}

    def factory(self, aClass, *pargs, **kargs):
        return aClass(*pargs, **kargs)

    def download_images(self):
        """ Initialize instances of ImageQuery and download images for
        search terms.

        Uses the ImageQuery method
        download_image_batches_for_search_term() to download images for
        each search term.
        """
        for search_term in self.search_term_list:
            image_query = self.factory(
                ImageQuery,
                search_term = search_term,
                driver_path = self.driver_path,
                chrome_options = self.chrome_options,
                number_files_wanted = self.number_files_wanted,
                search_url = self.search_url
                )
            image_query.download_images_for_search_term()


class ImageQuery():
    """Class that manages individual queries to Google Image to
    download images.

    Additional Instance variables:
        -thumbnail_list: List of all thumbnail WebElements in the viewing
        port of Chrome
        -search_url: String of search URL of Google Image Search Query
        with q="searchstring" replaced by q={q}
        -search_term_list: List of search terms
        -driver: Initialized Chrome Webdriver
        -DRIVER_PATH: path to chromedriver
        -number_files_wanted: Number of files to download for each search
        term
        -results: Empty dictionary that is filled with with keys equal
        to search terms and values containing a list of tuples of links
        and relative file paths on harddrive for successfully downloaded
        images
        -download_counter: integer used for enumerating the filenames
        when saving images on hard disk
        -thumbnail_nr: integer used for indexing current thumbnail
        in thumbnail_list
        -thumbnail: stores current WebElement of thumbnail on Google
        Search results page

    (Public) Methods:
        -.download_images(): Initialize instances of ImageQuery and
        use them to download images for search terms


    """
    def __init__(
        self,
        search_term,
        driver_path,
        chrome_options,
        number_files_wanted,
        search_url
        ):
        # self.driver = webdriver.Chrome(
        #     executable_path= driver_path,
        #     options= chrome_options
        #     )
        self.driver = webdriver.Remote("selenium_standalone_chrome:4444/wd/hub",
            options = chrome_options)
        self.number_files_wanted = number_files_wanted
        self.search_url = search_url
        self.number_files_downloaded = 0
        self.thumbnail_list = []
        self.thumbnail_list_current = []
        self.thumbnail_nr = 0
        self.thumbnail = None
        self.link = None
        self.relative_file_path = None
        self.search_url_plus_term = None
        self.wanted_height = None
        self.search_term = search_term

    def download_images_for_search_term(self):
        """ Download Images for a given seach_term.

        Steps:
            1. Search for images on google Images using the Chrome driver
            with self.search_term and self.search_url as an input
            2. While loop to download images with self.start_download_
            chain()

        Returns:
             True if successful
        """
        self.search_url_plus_term = self.search_url.format(q=f"{self.search_term}")
        self.driver.get(self.search_url_plus_term)

        logger.info("Searching for Images on Google Image using the following URL:"
            f"{self.search_url_plus_term}"
            )




        logger.info(
            f"Scanning the {self.number_files_wanted} needed WebElements"
            "for thumbnails on Google Image Result Page"
                )
        try:
            self.__get_thumbnail_list()
            logger.info(
                f"Managed to collect {len(self.thumbnail_list)} number of thumbnail"
                "WebElements"
                 )
        except NotEnoughResultsError:
            logger.error(
                f"Not enough thumbnail WebElements available in Google Image search results"
                f"Number of files wanted: {self.number_files_wanted}"
                f"vs. Number of thumbnails available: {len(self.thumbnail_list)}"
                " - Continuing with the number of thumbnails available"
                )
        except ScrollNotWorkingError:
            logger.error(
                "Scroll Down (window.scrollBy(x,y)) for __testing_end_of_page()"
                " not working. Please troubleshoot the code."
            )

        # deep copying the list of Thumbnail Webelements for use in
        # self.__download_nr_thumbnails()
        self.thumbnail_list_current = self.thumbnail_list[:]

        max_images_possible = max(
            len(self.thumbnail_list),
            self.number_files_wanted
            )

        logger.info(
            "Starting Downloads for the number of images possible after"
            f"using Google Image Search {max_images_possible}"
            )


        download_nr_success_tuple = self.__download_nr_thumbnails(
            max_images_possible
            )

        if download_nr_success_tuple[0]:
            logger.info(
                f"Successfully downloaded {max_images_possible} for search"
                f" term '{self.search_term}'"
                )
            self.driver.quit()
            return True
        else:
            logger.info(
                f"Only managed to download {download_nr_success_tuple[1]}"
                f" of {max_images_possible} images for search term '{self.search_term}'"
                )
            self.driver.quit()
            return False


    def __download_nr_thumbnails(self, number_thumbnails_requested):
        """ Recursively tries to download a certain number of requested images
        from the self.thumbnail_list by removing the topmost element of
        self.thumbnail_list after successfully downloading it and calling
        itself again, if not all images were downloaded as requested and
        there are still thumbnails in self.thumbnail_list

        Returns:
            (True, number_missing_images) if the number of thumbnails downloaded is as requested

            (False, number_missing_images), if the number of thumbnails
            successfully downloaded is less than requested
        """
        number_downloaded_images = 0

        for self.thumbnail_nr, self.thumbnail in enumerate(self.thumbnail_list_current):
            logger.info(
                f"Starting __Download_chain() for Thumbnail Nr."
                f" {self.thumbnail_list.index(self.thumbnail)}"
                f" of {number_thumbnails_requested}"
                )

            download_success_bool = self.__start_download_chain()

            if download_success_bool:
                number_downloaded_images +=1
                self.thumbnail_list_current.pop()

            if number_downloaded_images == number_thumbnails_requested:
                break

        number_missing_images = number_thumbnails_requested \
            - number_downloaded_images

        if len(self.thumbnail_list_current) == 0:
            return (False, number_missing_images)
        elif number_missing_images == 0:
            return (True, number_missing_images)
        else:
            self.__download_nr_thumbnails(number_missing_images)


    def __get_thumbnail_list(self):
        """ Saves all WebElements of the thumbnails on the
        Google Image Search results page to self.thumbnail_list

        Returns:
            True, if len(self.thumbnail_list) >= self.number_files_wanted

        Raises:
            NotEnoughResultsError: If there are not enough results on the
            google image search results page for the number of files wanted

        """

        while True:
            self.thumbnail_list = self.driver.find_elements_by_css_selector(
            "img.Q4LuWd")

            self.thumbnail = self.thumbnail_list[len(self.thumbnail_list) - 1]

            logger.info(
                "Scrolling to last thumbnail in self.thumbnail_list"
            )
            self.__scroll_to_thumbnail()

            logger.info(
                "Checking and clicking more images button"
            )
            self.__check_click_more_images_button()

            logger.info(
                "Checking whether end of Google Image Search page is reached"
            )
            if self.__testing_end_of_page():
                break

        if len(self.thumbnail_list) >= (self.number_files_wanted):
            return True

        else:
            raise NotEnoughResultsError


    def __start_download_chain(self):
        """ Try to download the image behind the thumbnail
        indexed by thumbnail_nr in the Google Image Search results
        page.

        Calls the following methods:
            2. self.scroll_to_thumbnail(): Scroll to WebElement.
            3. self.click_thumbnail(): Click WebElement to enter into closer
            view in Google Image results.
            4. self.__open_save_image(): Open Image in new tab and save to disk

        Expected exceptions in the scraping process are handled and
        logged here using the exceptions in self.expected_exceptions #todo

        Returns:
            [bool]: True, if download chain was successful.
                    False, if download chain was not successful.
        """
        #put expected exception in a class variable
        #Add: exception selenium.common.exceptions.JavascriptException(
        # msg=None, screen=None, stacktrace=None) for scroll_to_thumbnail
        expected_exception_tuple = (
            TimeoutException,
            ElementClickInterceptedException,
            NoSuchElementException,
            NotEnoughResultsError,
            StaleElementReferenceException,
            RequestException,
            KeyErrorNoContentTypeHTTPError,
            )

        try:
            logger.info(
                f"Scrolling to Thumbnail for Thumbnail Nr. {self.thumbnail_nr} "
                "on Google Image Result Page"
                )

            self.__scroll_to_thumbnail()

            logger.info(
                f"Clicking Thumbnail Nr. {self.thumbnail_nr} "
                "on Google Image Result Page"
                )

            self.__click_thumbnail()

            logger.info(
                f"Opening Thumbnail Nr. {self.thumbnail_nr} "
                f"in a new tab and saving to disk"
                )
            self.__open_save_image()

            return True
        except expected_exception_tuple as e:
            try:
                print(repr(e))
            except AttributeError:
                print("Attribute Error", e)
            return False
        return True


    def __scroll_to_thumbnail(self):
        """Scroll to thumbnail WebElement saved as self.thumbnail."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView(true);",
            self.thumbnail,
            )


    def __check_click_more_images_button(self):
        """ Click the "Show more Images"-Button on the Google Image
        search result page if possible.
        """
        #Wait until page is fully loaded
        WebDriverWait(self.driver, 5).until(
            lambda d: d.execute_script(
                'return document.readyState') == 'complete'
                )
        #checking for existence of "show more images"-button and click it
        try:
            show_more_images_button = self.driver.find_element_by_css_selector(
                "input.mye4qd"
                )
            print
            WebDriverWait(self.driver, 2).until(
            custom_expected_conditions.ElementClickableTest(
                show_more_images_button)).click()
        except NoSuchElementException:
            raise NoSuchElementException("Show More Images WebElement not found")
        except TimeoutException:
            logger.info(
                "Timeout for clickability of show more images WebElement -"
                "show more images button is probably not visible yet/anymore"
                )


    def __click_thumbnail(self):
        """ Clicks WebElement in self.thumbnail
        after waiting for WebElement to be clickable"""
        WebDriverWait(self.driver, 5).until(
            custom_expected_conditions.ElementClickableTest(self.thumbnail)
            ).click()

    def __open_save_image(self):
        """ Opens the image behind the thumbnail (that appears after thumbnail
        in Google Image search results is clicked) in a new tab and saves
        the image to disk
        """

        # store the ID of the original window
        original_window = self.driver.current_window_handle

        # get the image link
        self.__get_image_link()

        # open a new tab using self.link
        open_window_script = "window.open('" + self.link + "');"

        self.driver.execute_script(open_window_script)

        # wait for the new window or tab to open
        WebDriverWait(self.driver,5).until(EC.number_of_windows_to_be(2))


        # loop trhough until we find a new window handle and switch focus to it
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                break

        # wait until the img has been loaded
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script(
                'return document.readyState') == 'complete'
                )

        img_element = self.driver.find_element_by_css_selector("img")

        name_of_file = f"{self.search_term}" + "_" + f"{self.thumbnail_nr}"

        img_element.screenshot(name_of_file)

        # close opened tab
        self.driver.close()

        # switch focus back to original window
        self.driver.switch_to.window(original_window)

        return True

    def __get_image_link(self):
        """
        Extracts the image link behind a clicked thumbnail (self.thumbnail)
        in Google Image results and saves it under self.link

        Returns:
            True, if no exceptions are raised
        Details:
            WebDriverWait with wait.until(ElementSrcString()) is needed,
            because sometimes at first the src is a data url
            (e.g. data:image/gif;base64,R0lGOD...). An if-clause is
            needed, because the css selector 'img.n3VNCb' selects a list
            of three images on the result page: the previous one([0]),
            the current one[1] and the next one[2]. For the
            thumbnail_nr == 0 the previous one does not exist,
            which moves the current one to [0] of the list.
        """
        if self.thumbnail_nr == 0:
            element = WebDriverWait(self.driver, 5).until(
                custom_expected_conditions.ElementSrcString(
                    (By.CSS_SELECTOR, 'img.n3VNCb'),
                    "http",
                    "encrypted-tbn0.gstatic.com",
                    0,
                    self.driver,
                    )
                )
            self.link = element.get_attribute('src')
        else:
            element = WebDriverWait(self.driver, 5).until(
                custom_expected_conditions.ElementSrcString(
                    (By.CSS_SELECTOR, 'img.n3VNCb'),
                    "http",
                    "encrypted-tbn0.gstatic.com",
                    1,
                    self.driver,
                    )
                )
            self.link = element.get_attribute('src')
        return True


    def __testing_end_of_page(self):
        """Tests whether the end of the page of google image search
        results is reached

        Returns:
            True: If end of page is reached
            False: If end of page is not reached
        """

        #Wait until page is fully loaded
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script(
                'return document.readyState') == 'complete'
                )

        #recording the height of the page
        old_height = self.driver.execute_script(
            "return window.scrollY"
            )

        new_height = old_height

        max_scroll_height = self.driver.execute_script(
            "return document.body.scrollHeight;"
            )


        # for loop to deal with the problem that sometimes window.scrollBy(0,10)
        # does not work on the first try (for unknown reasons)
        for i in range(20):
            self.driver.execute_script("window.scrollBy(0,10);")

            new_height = self.driver.execute_script(
                "return pageYOffset"
                )

            if old_height < new_height:
                break

            # + 2000 to account for a margin of error because max_scroll_height
            # is bigger than maximum pageYOffset reachable through scrolling
            if i == 19 and max_scroll_height > new_height + 2000:
                 raise ScrollNotWorkingError


        # waiting until scroll down has been successful by testing
        # whether old_height =! new_height
        try:
            WebDriverWait(self.driver, 2).until(
                custom_expected_conditions.ScrollSuccessTest(
                    old_height,
                    self.driver,
                    )
                )
        except TimeoutException:
            logger.info
            (
                f"{TimeoutException} Scrolling down had no effect after waiting"
                " 2 seconds - End of page reached"
            )
            return True
        else:
            return False

CHROME_OPTIONS = Options()

# chrome_options.add_argument("--window-size=1920,1080")
CHROME_OPTIONS.add_argument('--headless')
CHROME_OPTIONS.add_argument('--no-sandbox')
CHROME_OPTIONS.add_argument('--disable-dev-shm-usage')
CHROME_OPTIONS.add_argument('window-size=1920x1480')

DRIVER_PATH = './chromedriver_dir/chromedriver'
SEARCH_URL = """https://www.google.com/search?as_st=y&tbm=isch&hl=en&as_q={q}&as
epq=&as_oq=&as_eq=&cr=&as_sitesearch=&safe=images&tbs=itp:photo"""


testrun = GoogleImageScraper(
    search_url = SEARCH_URL,
    search_term_list =["kitten"],
    DRIVER_PATH = DRIVER_PATH,
    number_files_wanted = 700,
    chrome_options = CHROME_OPTIONS
    )

testrun.download_images()

