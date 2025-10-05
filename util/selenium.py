import logging
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class SeleniumManager:
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.driver = None

    def get_driver(self):
        if self.driver:
            return self.driver
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Remote(
                command_executor="http://selenium:4444/wd/hub", 
                options=options
            )
            logger.info("Remote driver created successfully")
        except Exception as e:
            logger.warning(f"Remote driver failed: {e}")
            try:
                self.driver = webdriver.Chrome(options=options)
                logger.info("Local driver created successfully")
            except Exception as local_e:
                logger.error(f"Both drivers failed: {local_e}")
                return None
        
        self.driver.set_page_load_timeout(60)
        self.driver.implicitly_wait(5) 
        
        try:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            logger.warning(f"Could not execute stealth script: {e}")
        
        return self.driver

    def safe_get(self, url, max_retries=3):
        driver = self.get_driver()
        if not driver:
            return False
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Navigating to {url} (attempt {attempt + 1}/{max_retries})")
                driver.get(url)
                
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                time.sleep(5)
                
                self.dismiss_popups()
                
                WebDriverWait(driver, 10).until(
                    ec.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                logger.info("Page loaded successfully")
                return True
                
            except Exception as e:
                logger.error(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)  
                    continue
                return False
        
        return False

    def wait_for_elements(self, by, selector, timeout=None, log_page_source=True):
        if not self.driver:
            return None
        
        timeout = timeout or self.timeout
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                ec.visibility_of_element_located((by, selector))
            )
            logger.info(f"Element found: {selector}")
            return element
            
        except TimeoutException:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((by, selector))
                )
                logger.warning(f"Element present but not visible: {selector}")
                return element
            except TimeoutException:
                logger.error(f"Element not found: {selector}")
                
                if log_page_source:
                    try:
                        page_source = self.driver.page_source
                        logger.debug(f"Page URL: {self.driver.current_url}")
                        logger.debug(f"Page title: {self.driver.title}")
                        logger.debug(f"Page source (first 2000 chars): {page_source[:2000]}")
                        
                        similar_classes = self.driver.execute_script("""
                            const elements = document.querySelectorAll('[class*="Box"]');
                            return Array.from(elements).map(el => el.className).slice(0, 10);
                        """)
                        logger.debug(f"Classes containing 'Box': {similar_classes}")
                    except Exception as debug_e:
                        logger.warning(f"Could not log debug info: {debug_e}")
                
                return None
                
        except Exception as e:
            logger.error(f"Error finding element {selector}: {e}", exc_info=True)
            return None

    def wait_for_any_elements(self, selectors, timeout=None):
        if not self.driver:
            return None, None
        
        timeout = timeout or self.timeout
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            for by, selector in selectors:
                try:
                    element = self.driver.find_element(by, selector)
                    if element.is_displayed():
                        logger.info(f"Found element with selector: {selector}")
                        return element, selector
                except:
                    continue
            time.sleep(0.5)
        
        logger.error(f"None of the selectors found: {selectors}")
        return None, None

    def dismiss_popups(self):
        if not self.driver:
            return
        
        try:
            # Handle JS alerts or confirms
            try:
                alert = self.driver.switch_to.alert
                alert.dismiss()
                logger.info("JavaScript alert dismissed")
            except:
                pass  # No alert found

            # Common cookie consent buttons
            possible_selectors = [
                (By.XPATH, "//button[contains(text(), 'Accept')]"),
                (By.XPATH, "//button[contains(text(), 'OK')]"),
                (By.XPATH, "//button[contains(text(), 'Agree')]"),
                (By.XPATH, "//button[contains(@id, 'accept')]"),
                (By.XPATH, "//button[contains(@class, 'accept')]"),
                (By.XPATH, "//div[contains(@class, 'cookie')]//button"),
            ]
            
            for by, sel in possible_selectors:
                try:
                    el = WebDriverWait(self.driver, 2).until(ec.element_to_be_clickable((by, sel)))
                    el.click()
                    logger.info(f"Dismissed popup via selector: {sel}")
                    time.sleep(1)
                    break
                except:
                    continue
            
            # Common modal close buttons
            modal_close_selectors = [
                (By.CSS_SELECTOR, "[aria-label='Close']"),
                (By.CSS_SELECTOR, ".modal-close, .close, .btn-close"),
                (By.XPATH, "//button[contains(text(), 'Close')]"),
                (By.XPATH, "//div[contains(@class, 'modal')]//button"),
            ]
            
            for by, sel in modal_close_selectors:
                try:
                    el = WebDriverWait(self.driver, 2).until(ec.element_to_be_clickable((by, sel)))
                    el.click()
                    logger.info(f"Closed modal with selector: {sel}")
                    time.sleep(1)
                    break
                except:
                    continue

        except Exception as e:
            logger.warning(f"Failed to dismiss popups: {e}")

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
            finally:
                self.driver = None