# pyright: reportMissingImports=false
from contextlib import contextmanager, suppress
import importlib
import os
from typing import Optional


DEFAULT_WAIT_SECONDS = 30


def build_chrome_options(user_agent: Optional[str] = None, headless: bool = True):
    options_module = importlib.import_module("selenium.webdriver.chrome.options")
    Options = getattr(options_module, "Options")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    return options


@contextmanager
def selenium_session(
    *,
    command_executor: Optional[str] = None,
    headless: bool = True,
    page_load_timeout_seconds: int = 30,
    user_agent: Optional[str] = None,
):
    selenium_module = importlib.import_module("selenium")
    webdriver = getattr(selenium_module, "webdriver")
    driver = None
    try:
        executor = command_executor or os.getenv("SELENIUM_REMOTE_URL", "http://selenium:4444/wd/hub")
        options = build_chrome_options(user_agent=user_agent, headless=headless)
        driver = webdriver.Remote(command_executor=executor, options=options)
        driver.set_page_load_timeout(page_load_timeout_seconds)
        yield driver
    finally:
        if driver is not None:
            with suppress(Exception):
                driver.quit()


def wait_for_visible(driver, by, value: str, timeout_seconds: int = DEFAULT_WAIT_SECONDS):
    support_module = importlib.import_module("selenium.webdriver.support")
    EC = getattr(support_module, "expected_conditions")
    ui_module = importlib.import_module("selenium.webdriver.support.ui")
    WebDriverWait = getattr(ui_module, "WebDriverWait")
    return WebDriverWait(driver, timeout_seconds).until(EC.visibility_of_element_located((by, value)))


def wait_for_present(driver, by, value: str, timeout_seconds: int = DEFAULT_WAIT_SECONDS):
    support_module = importlib.import_module("selenium.webdriver.support")
    EC = getattr(support_module, "expected_conditions")
    ui_module = importlib.import_module("selenium.webdriver.support.ui")
    WebDriverWait = getattr(ui_module, "WebDriverWait")
    return WebDriverWait(driver, timeout_seconds).until(EC.presence_of_element_located((by, value)))


def wait_for_clickable(driver, by, value: str, timeout_seconds: int = DEFAULT_WAIT_SECONDS):
    support_module = importlib.import_module("selenium.webdriver.support")
    EC = getattr(support_module, "expected_conditions")
    ui_module = importlib.import_module("selenium.webdriver.support.ui")
    WebDriverWait = getattr(ui_module, "WebDriverWait")
    return WebDriverWait(driver, timeout_seconds).until(EC.element_to_be_clickable((by, value)))


