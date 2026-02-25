import os
import requests
import csv
from dotenv import load_dotenv

load_dotenv()

SHOP_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN_PHONETRADE") ##
API_VERSION = os.getenv("SHOPIFY_ADMIN_API_VERSION")
ACCESS_TOKEN = os.getenv("SHOPIFY_ADMIN_API_TOKEN_PHONETRADE") ##

HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def fetch_all_products():
    """
    Henter alle produkter og deres varianter via paginering.
    Returnerer liste over variant-data.
    """
    print("🔄 Henter ALLE produkter fra Shopify...")

    all_variants = []
    url = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/products.json?limit=250"
    
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Fejl: {response.status_code} – {response.text}")
            break

        products = response.json().get("products", [])
        print(f"✅ Hentede {len(products)} produkter...")

        for product in products:
            variant_data = {
                "Produktnavn": product.get("title", ""),
                "Produkt ID": product.get("id", ""),
                "Produkt Status": product.get("status", ""),
            }
            all_variants.append(variant_data)

        # Shopify paginering (Link-header)
        link_header = response.headers.get("Link", "")
        next_url = None
        if 'rel="next"' in link_header:
            parts = link_header.split(",")
            for part in parts:
                if 'rel="next"' in part:
                    next_url = part.split(";")[0].strip().strip("<>").strip()
        url = next_url

    return all_variants

def write_to_csv(variants, filename="phonetrade_products_status.csv"): ##
    """Skriver variant-data til en CSV-fil."""
    if not variants:
        print("⚠️ Ingen varianter at gemme.")
        return
    
    print(f"💾 Skriver data til {filename}...")
    fieldnames = list(variants[0].keys())

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(variants)
    
    print(f"✅ Færdig! Gemte {len(variants)} produkter i {filename}")

if __name__ == "__main__":
    variants = fetch_all_products()
    write_to_csv(variants)
