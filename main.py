from playwright.sync_api import sync_playwright
import re
import sqlite3
from datetime import datetime

def get_ripley_price(product_url):
    """Scrape product name and price from a Ripley Peru product page."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        print(f"Loading {product_url[:80]}...")
        page.goto(product_url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        # Extract product data from the DOM
        data = page.evaluate("""() => {
            const title = document.querySelector('h1')?.textContent?.trim() || null;

            // Main price: .product-price inside .product-internet-price
            const priceEl = document.querySelector(
                '.product-internet-price .product-price'
            );
            const priceText = priceEl?.textContent?.trim() || null;

            const skuEl = document.querySelector(
                '.sku-container .sku-value'
            );
            const skuText = skuEl?.textContent?.trim() || null;

            return { title, priceText, skuText };
        }""")

        browser.close()

        # Parse the numeric price from text like "S/ 499"
        price = None
        if data["priceText"]:
            match = re.search(r"[\d,.]+", data["priceText"].replace("\xa0", ""))
            if match:
                price = float(match.group().replace(",", ""))

        return {
            "sku": data["skuText"],
            "title": data["title"],
            "price": price,
            "url": product_url,
            "date": str(datetime.now())
        }

def save_product(product):
    if product["price"] is None:
        print("Failed to extract the price. The page structure may have changed.")
        return

    with sqlite3.connect("tracker.db") as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS products_diego "
            "(sku TEXT, title TEXT, price REAL, url TEXT, date TEXT)"
        )
        conn.execute(
            "INSERT INTO products_diego (sku, title, price, url, date) "
            "VALUES (?, ?, ?, ?, ?)",
            (product["sku"], product["title"], product["price"],
             product["url"], product["date"]),
        )


# --- Usage ---
url = (
    "https://simple.ripley.com.pe/casaca-algodon-hombre-levis-type-3-sherpa-trucker-"
    "2016361145647?color_80=azul&cat=casacas_hombre_ic&pos=46&p=1&ps=48&s=mdco"
)
result = get_ripley_price(url)

save_product(result)


