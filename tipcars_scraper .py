import requests, sqlite3, time
from bs4 import BeautifulSoup

def scrape_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    offers = soup.find_all("div", class_="inzerat")

    for offer in offers:
        vin_tag = offer.find("span", class_="vin")
        vin = vin_tag.text.strip() if vin_tag else None

        make_model = offer.find("h2")
        if make_model:
            parts = make_model.text.strip().split(" ", 1)
            make = parts[0]
            model = parts[1] if len(parts) > 1 else ""
        else:
            make = model = ""

        year_tag = offer.find("li", string=lambda x: x and "Rok výroby" in x)
        year = year_tag.text.strip()[-4:] if year_tag else ""

        price_tag = offer.find("strong", class_="cena")
        price = int(price_tag.text.replace(" ", "").replace("\xa0", "")) if price_tag else 0

        if vin:
            c.execute("INSERT OR REPLACE INTO vehicles (vin, make, model, year, price) VALUES (?, ?, ?, ?, ?)",
                      (vin, make, model, year, price))

    conn.commit()

conn = sqlite3.connect("vehicles_tipcars.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS vehicles (
                vin TEXT PRIMARY KEY,
                make TEXT,
                model TEXT,
                year TEXT,
                price INTEGER)""")

for page in range(1, 1001):  # změň na 70001 pro 70 000 stránek
    print(f"Načítám stránku {page}")
    scrape_page(f"https://www.tipcars.com/osobni-auto/?strana={page}")
    time.sleep(2)

conn.close()
print("Hotovo. Data uložena do vehicles_tipcars.db.")
