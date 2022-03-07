from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from requests.exceptions import RequestException

class KeyErrorNoContentTypeHTTPError(KeyError):
    """A KeyError Exception was raised, because the header of the response
    object had no content-type key."""
    def __init__(
        self,
        message="""A KeyError Exception was raised, because the header of the response
        object had no content-type key."""):
        self.message = message
        print (self.message)
        super().__init__(self.message)


class TimeoutExceptionShowMoreImagesButton(TimeoutException):
    """A TimeoutException was raised for the Show more Images Button
    on the Google Image Search Results page"""
    def __init__(
        self,
        message="""A TimeoutException was raised for
        the Show more Images Button on the Google Image Search Results
        page"""):
        self.message = message
        print (self.message)
        super().__init__(self.message)


class NoSuchElementExceptionShowMoreImagesButton(NoSuchElementException):
    """A NoSuchElementException was raised for the 'Show more Images Button
    on the Google Image Search Results page"""
    def __init__(
        self,
        message="""A NoSuchElementException was raised for the 'Show more
        Images Button on the Google Image Search Results page"""):
        self.message = message
        print (self.message)
        super().__init__(self.message)

class NotEnoughResultsError(Exception):
    """There are not not enough results on the Google Image Search Results
    page"""
    def __init__(
        self,
        message="""There are not not enough results on the Google Image
        Search Results page"""):
        self.message = message
        print (self.message)
        super().__init__(self.message)




class ScrollNotWorkingError(Exception):
    """Scroll Down for __testing_end_of_page() not working after 20 tries"""
    def __init__(
        self,
        message="""Scroll Down for __testing_end_of_page() not working after 20 tries"""):

        self.message = message

        print (self.message)
        super().__init__(self.message)

class FileTypeNotImage(RequestException):
    """File type of downloaded file is not image/jpeg"""
    def __init__(
        self,
        message="""File type of downloaded file is not image/jpeg"""):
        self.message = message
        print (self.message)
        super().__init__(self.message)