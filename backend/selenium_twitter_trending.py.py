from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pymongo import MongoClient
from datetime import datetime
import uuid
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["trending_topics"]
collection = db["twitter_trends"]

proxy_user = os.getenv("PROXYMESH_USER")
proxy_pass = os.getenv("PROXYMESH_PASS")

if not proxy_user or not proxy_pass:
    raise ValueError("ProxyMesh credentials are missing. Please set PROXYMESH_USER and PROXYMESH_PASS in the environment variables.")

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

proxy_address = f"{proxy_user}:{proxy_pass}@proxy.proxy-mesh.com:31280"
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = proxy_address
proxy.ssl_proxy = proxy_address

options.set_preference("network.proxy.type", 1)
options.set_preference("network.proxy.http", proxy_address.split('@')[1].split(':')[0])
options.set_preference("network.proxy.http_port", int(proxy_address.split(':')[-1]))
options.set_preference("network.proxy.ssl", proxy_address.split('@')[1].split(':')[0])
options.set_preference("network.proxy.ssl_port", int(proxy_address.split(':')[-1]))

def fetch_trending_topics():
    """
    Fetch the top 5 trending topics and the current IP address used for scraping.
    """
    driver = None
    try:
        service = Service()  
        driver = webdriver.Firefox(service=service, options=options)
        
        driver.get("https://x.com")
        print("Accessing X (Twitter)...")
        
        try:
            trending_section = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//section[contains(., \"What’s happening\")]")
                )
            )
            trends = trending_section.find_elements(
                By.XPATH, ".//span[contains(@class, 'css-901oao')]"
            )
            top_trends = [trend.text for trend in trends[:5]]
        except TimeoutException:
            print("Timeout waiting for the trending section.")
            top_trends = []
        except NoSuchElementException:
            print("Trending section not found.")
            top_trends = []

        driver.get("https://api.ipify.org?format=text")
        ip_address = driver.find_element(By.TAG_NAME, "body").text.strip()

    except Exception as e:
        print("Error initializing WebDriver:", e)
        top_trends, ip_address = [], None
    finally:
        if driver:
            driver.quit()

    return top_trends, ip_address

def store_results(trends, ip_address):
    """
    Store the fetched results into MongoDB.
    """
    unique_id = str(uuid.uuid4())
    end_time = datetime.now()

    record = {
        "unique_id": unique_id,
        "trend1": trends[0] if len(trends) > 0 else None,
        "trend2": trends[1] if len(trends) > 1 else None,
        "trend3": trends[2] if len(trends) > 2 else None,
        "trend4": trends[3] if len(trends) > 3 else None,
        "trend5": trends[4] if len(trends) > 4 else None,
        "date_time": end_time,
        "ip_address": ip_address
    }

    collection.insert_one(record)
    print("Record stored:", record)

if __name__ == "__main__":
    trends, ip_address = fetch_trending_topics()
    if trends and ip_address:
        store_results(trends, ip_address)
    else:
        print("Failed to fetch data. Please check the logs.")
