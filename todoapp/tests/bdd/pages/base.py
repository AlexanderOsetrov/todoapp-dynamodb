from time import sleep
from collections import namedtuple
from selenium.webdriver.common.by import By
from todoapp.tests.utils.utils import logger
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (StaleElementReferenceException, TimeoutException)


class Locator:

    Locator = namedtuple("Locator", "by value")

    @classmethod
    def by_css(cls, value):
        return cls.Locator(By.CSS_SELECTOR, value)

    @classmethod
    def by_id(cls, value):
        return cls.Locator(By.ID, value)

    @classmethod
    def by_name(cls, value):
        return cls.Locator(By.NAME, value)

    @classmethod
    def by_xpath(cls, value):
        return cls.Locator(By.XPATH, value)


class BasePage:

    def __init__(self, driver):
        self.driver: WebDriver = driver

    @staticmethod
    def wait(timeout):
        sleep(timeout)

    def open_page(self, url):
        logger.info("Opening the page: %s" % url)
        self.driver.get(url)

    def find(self, locator) -> WebElement:
        logger.info("Searching for an element located at '%s' using '%s' strategy" % (locator.value, locator.by))
        return self.driver.find_element(locator.by, locator.value)

    def click_element(self, locator, retry=5, retry_interval=1, use_action_chains=False):
        while True:
            try:
                if use_action_chains:
                    element = self.find(locator)
                    ActionChains(self.driver).move_to_element(element).click().perform()
                    break
                else:
                    element = self.find(locator)
                    element.click()
                    break
            except StaleElementReferenceException:
                logger.debug("Element is stale")
                retry -= 1
                sleep(retry_interval)
                if retry <= 0:
                    raise

    def doubleclick_element(self, locator, retry=5, retry_interval=1):
        while True:
            try:
                element = self.find(locator)
                ActionChains(self.driver).move_to_element(element).double_click().perform()
                break
            except StaleElementReferenceException:
                logger.debug("Element is stale")
                retry -= 1
                sleep(retry_interval)
                if retry <= 0:
                    raise

    def input_text(self, locator, text, auto_clear=False, retry=5, retry_interval=1):
        while True:
            try:
                element = self.find(locator)
                logger.info("Inserting text '%s' into the element located at '%s'" % (text, locator.value))
                if auto_clear:
                    element.clear()
                    element.send_keys(text)
                else:
                    element.send_keys(text)
                break
            except StaleElementReferenceException:
                logger.debug("Element is stale")
                retry -= 1
                sleep(retry_interval)
                if retry <= 0:
                    raise

    def clear_text(self, locator, retry=5, retry_interval=1):
        while True:
            try:
                self.find(locator).clear()
                break
            except StaleElementReferenceException:
                logger.debug("Element is stale")
                retry -= 1
                sleep(retry_interval)
                if retry <= 0:
                    raise

    def press_keys(self, locator, keys):
        selenium_escape = Keys()
        keys_to_send = []
        for key in keys.split("+"):
            try:
                keys_to_send.append(getattr(selenium_escape, key))
            except AttributeError:
                keys_to_send.append(key)
        if locator:
            self.find(locator).send_keys(*keys_to_send)
        else:
            ActionChains(self.driver).send_keys(*keys_to_send).perform()

    def get_element_text(self, locator, retry=5, retry_interval=1):
        while True:
            try:
                element_text = self.find(locator).text
                logger.debug("Element text: '%s'" % element_text)
                return element_text
            except StaleElementReferenceException:
                logger.debug("Element is stale")
                retry -= 1
                if retry <= 0:
                    raise

    def is_element_visible(self, locator):
        while True:
            try:
                element = self.find(locator)
                if element.is_displayed():
                    logger.debug(f"Element located at '{locator.value}' is visible")
                    return True
                else:
                    logger.debug(f"Element located at '{locator.value}' is not visible")
                    return False
            except StaleElementReferenceException:
                logger.debug("Element is stale")

    def is_element_present(self, locator, timeout=5):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                ec.presence_of_element_located(locator))
            if element is not None:
                logger.info(f"The element located at '{locator.value}' presents on the DOM")
                return True
            else:
                return False
        except TimeoutException:
            logger.info(f"The element located at '{locator.value}' does not present on the DOM")
            return False

    def wait_for(self, condition, timeout):
        return WebDriverWait(self.driver, timeout).until(condition)

    def wait_for_visibility_of(self, locator, timeout=60):
        logger.info("Waiting for visibility of the element located at: '%s'" % locator.value)
        return self.wait_for(ec.visibility_of_element_located(locator), timeout)

    def wait_for_presence_of(self, locator, timeout=60):
        logger.info("Waiting for presence of the element located at: '%s'" % locator.value)
        return self.wait_for(ec.presence_of_element_located(locator), timeout)

    def wait_for_invisibility_of(self, locator, timeout=60):
        logger.info("Waiting for invisibility of the element located at: '%s'" % locator.value)
        return self.wait_for(ec.invisibility_of_element_located(locator), timeout)

    def hover_mouse_over(self, locator, retry=10, retry_interval=1, use_javascript=False):
        while True:
            try:
                element = self.find(locator)
                if use_javascript:
                    jscript = "var element = arguments[0]; var mouseEventObj = " \
                              "document.createEvent('MouseEvents'); " \
                              "mouseEventObj.initEvent( 'mouseover', true, true ); " \
                              "element.dispatchEvent(mouseEventObj);"
                    self.driver.execute_script(jscript, element)
                    return True
                else:
                    ActionChains(self.driver).move_to_element(element).perform()
                    return True
            except StaleElementReferenceException:
                logger.debug("Element is stale")
                retry -= 1
                sleep(retry_interval)
                if retry == 0:
                    raise

    def execute_java_script(self, script, *args):
        logger.debug(f'Executing JavaScript: {script}')
        return self.driver.execute_script(script, *args)

    def get_attribute(self, locator, attribute):
        while True:
            try:
                attribute_value = self.find(locator,).get_attribute(attribute)
                logger.debug(f"Element attribute '{attribute}' value: '{attribute_value}'")
                return attribute_value
            except StaleElementReferenceException:
                logger.debug("Element is stale")
