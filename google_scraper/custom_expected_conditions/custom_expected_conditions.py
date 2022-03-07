class ElementClickableTest(): # pylint: disable=too-few-public-methods
    """ An Expectation for checking if an element is visible and enabled
    such that you can click it. The standard class is modified to accept
    an element as an argument, because the standard CSS locator does not
    uniquely identify the relevant element
    """
    def __init__(self, element):
        self.element = element

    def __call__(self, driver):
        cond1 = self.element.is_displayed()
        cond2 = self.element.is_enabled()
        if cond1 and cond2:
            return self.element
        else:
            return False

class ScrollSuccessTest(object):
    """ An Expectation for checking if a scroll down has been successful
    by comparing whether old_height before scroll down
    (= old_height_test) and new_height of document.body.scrollHeight
    after scroll down are different
        Args:
            old_height: Height before scroll down
        Returns:
            True: If old_height is different from new_height
            False: if old_height == new_height
    """
    def __init__(self, old_height, driver):
        self.old_height = old_height
        self.driver = driver
    def __call__(self, driver):
        new_height = self.driver.execute_script(
            "return window.scrollY"
            )
        if self.old_height != new_height:
            return True
        else:
            return False


class ElementSrcString(object):
    """An expectation for checking that an element has string1 in the
    "src" attribute and string2 not in the "src" attribute (=proper link).

    Args:
        locator ([Locator Object]): [Locator used to find the element]
        string1 ([string]): string that is supposed to be in the src
            attribute
        string2 ([string]): String that is not supposed to be in the src
            attribute
        position ([int]): Positional index of element to be found
        driver: Initialized Webdriver

    Returns:
        [WebElement]: [WebElement that has a proper link]

    Raises:
        NoSuchElementException: If WebElement with a proper link cannot
            be found
    """

    def __init__(self, locator, string1, string2, position, driver):
        self.locator = locator
        self.string1 = string1
        self.string2 = string2
        self.driver = driver
        self.position = position

    def __call__(self, driver):
        # Finding the referenced element
        element = self.driver.find_elements(*self.locator)[self.position]
        cond1 = self.string1 in element.get_attribute("src")
        cond2 = not self.string2 in element.get_attribute("src")
        if cond1 and cond2:
            return element
        else:
            return False
