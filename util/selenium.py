import logging
import time
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
from config.settings import base

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)

class SeleniumManager:
    
    def __init__(self, max_retries=3, retry_delay=2):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.driver = None
    
    def get_driver(self):
        options = Options()
        
        # Enhanced Chrome options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Window size and user agent
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Memory and performance optimizations
        options.add_argument("--memory-pressure-off")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        
        for attempt in range(self.max_retries):
            try:
                self.driver = webdriver.Remote(
                    command_executor="http://selenium:4444/wd/hub",
                    options=options
                )
                
                # Enhanced timeouts and settings
                self.driver.set_page_load_timeout(60)
                self.driver.implicitly_wait(15)
                self.driver.set_window_size(1920, 1080)
                
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                logger.info(f"Remote Selenium driver initialized successfully on attempt {attempt + 1}")
                return self.driver
                
            except Exception as e:
                logger.warning(f"Remote driver attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  
                else:
                    try:
                        self.driver = webdriver.Chrome(options=options)
                        self.driver.set_page_load_timeout(60)
                        self.driver.implicitly_wait(15)
                        logger.info("Fallback to local Chrome driver successful")
                        return self.driver
                    except Exception as local_e:
                        logger.error(f"Both remote and local drivers failed: {local_e}")
                        return None
        
        return None
    
    def safe_get(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                if not self.driver:
                    raise WebDriverException("Driver not initialized")
                
                self.driver.get(url)
                WebDriverWait(self.driver, 20).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                time.sleep(random.uniform(1, 3))
                return True
                
            except Exception as e:
                logger.warning(f"Navigation attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delay)
                    try:
                        self.driver.refresh()
                        time.sleep(2)
                    except:
                        pass
        
        return False
    
    def wait_for_elements(self, by, element_identifier, timeout=20, multiple=False):
        strategies = [
            lambda: WebDriverWait(self.driver, timeout).until(
                ec.presence_of_element_located((by, element_identifier))
            ),
            lambda: WebDriverWait(self.driver, timeout).until(
                ec.visibility_of_element_located((by, element_identifier))
            ),
            lambda: WebDriverWait(self.driver, timeout//2).until(
                ec.element_to_be_clickable((by, element_identifier))
            )
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                element = strategy()
                logger.info(f"Element {element_identifier} found using strategy {i + 1}")
                
                if multiple:
                    return self.driver.find_elements(by, element_identifier)
                return element
                
            except TimeoutException:
                logger.warning(f"Strategy {i + 1} failed for {element_identifier}")
                continue
            except Exception as e:
                logger.warning(f"Strategy {i + 1} error for {element_identifier}: {e}")
                continue
        
        try:
            if by == By.XPATH:
                elements = self.driver.execute_script(f"""
                    var xpath = "{element_identifier}";
                    var result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                    return result.singleNodeValue;
                """)
                if elements:
                    logger.info(f"Element {element_identifier} found via JavaScript")
                    return elements if not multiple else [elements]
        except Exception as e:
            logger.warning(f"JavaScript fallback failed: {e}")
        
        logger.error(f"All strategies failed for {element_identifier}")
        return None if not multiple else []
    
    def scroll_to_element(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"Could not scroll to element: {e}")
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium driver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
            finally:
                self.driver = None
