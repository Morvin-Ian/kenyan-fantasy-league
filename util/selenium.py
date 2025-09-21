import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

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
        
        try:
            self.driver = webdriver.Remote(
                command_executor="http://selenium:4444/wd/hub",
                options=options
            )
            logger.info("Remote driver created successfully")
        except Exception as e:
            logger.warning(f"Remote driver failed: {e}")
            try:
                # Fallback to local
                self.driver = webdriver.Chrome(options=options)
                logger.info("Local driver created successfully")
            except Exception as local_e:
                logger.error(f"Both drivers failed: {local_e}")
                return None
        
        # Basic timeouts only
        self.driver.set_page_load_timeout(60)
        self.driver.implicitly_wait(10)
        return self.driver
    
    def safe_get(self, url):
        """Navigate to URL"""
        driver = self.get_driver()
        if not driver:
            return False
            
        try:
            logger.info(f"Navigating to {url}")
            driver.get(url)
            time.sleep(2)  # Simple wait for page load
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    def wait_for_elements(self, by, selector, timeout=None):
        """Wait for element to appear"""
        if not self.driver:
            return None
            
        timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                ec.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {selector}")
            return None
        except Exception as e:
            logger.error(f"Error finding element {selector}: {e}")
            return None
    
    def close(self):
        """Close the driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
            finally:
                self.driver = None