import os
import requests
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

SHOPIFY_API_VERSION = os.getenv("SHOPIFY_ADMIN_API_VERSION")

def get_variants_from_store(shop_key):
    domain_env = f"SHOPIFY_STORE_DOMAIN_{shop_key.upper()}"
    token_env = f"SHOPIFY_ADMIN_API_TOKEN_{shop_key.upper()}"
    store_domain = os.getenv(domain_env)
    access_token = os.getenv(token_env)

    if not store_domain or not access_token:
        raise ValueError(f"❌ Mangler Shopify credentials for {shop_key} i .env")

    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
    }

    variants = []
    page_info = None
    base_url = f"https://{store_domain}/admin/api/{SHOPIFY_API_VERSION}/products.json?limit=250"

    print(f"📥 Henter produkter fra {shop_key}...")

    while True:
        url = base_url if not page_info else f"{base_url}&page_info={page_info}"
        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            raise Exception(f"❌ Fejl ved GET {shop_key}: {resp.text}")

        products = resp.json().get("products", [])
        for product in products:
            for variant in product.get("variants", []):
                variant_data = {
                    "variant_id": str(variant["id"]),
                    "product_title": product["title"],
                    "variant_title": variant["title"],
                    "sku": variant["sku"],
                    "composite_key": (product["title"] + variant["title"]).replace(" ", "").lower(),
                }
                variants.append(variant_data)

        # Shopify pagination (Link header)
        link_header = resp.headers.get("Link")
        if link_header and 'rel="next"' in link_header:
            page_info = link_header.split("page_info=")[1].split(">")[0]
        else:
            break

    print(f"✅ {len(variants)} varianter hentet fra {shop_key}")
    return variants

def check_uniqueness(variants, shop_key):
    print(f"\n🔍 Tjekker SKU-unikhed for {shop_key}...")
    skus = [v["sku"] for v in variants]
    empty_skus = [v for v in variants if not v["sku"]]
    duplicate_skus = set([sku for sku in skus if skus.count(sku) > 1 and sku])

    if empty_skus:
        print(f"❌ {len(empty_skus)} SKU'er mangler i {shop_key}")
    else:
        print(f"✅ Ingen tomme SKU'er i {shop_key}")

    if duplicate_skus:
        print(f"❌ Fundet {len(duplicate_skus)} duplikerede SKU'er i {shop_key}: {list(duplicate_skus)[:5]}...")
    else:
        print(f"✅ Alle SKU'er er unikke i {shop_key}")

def compare_composite_keys(green_variants, phonetrade_variants):
    print("\n🔗 Sammenligner fælles Composite Keys...")

    green_map = {v["composite_key"]: v for v in green_variants}
    phonetrade_map = {v["composite_key"]: v for v in phonetrade_variants}

    shared_keys = set(green_map.keys()) & set(phonetrade_map.keys())

    mismatches = []
    for key in shared_keys:
        sku1 = green_map[key]["sku"]
        sku2 = phonetrade_map[key]["sku"]
        if sku1 != sku2:
            mismatches.append((key, sku1, sku2))

    if mismatches:
        print(f"❌ {len(mismatches)} produkter med samme Composite Key har forskellige SKU'er:")
        for key, sku1, sku2 in mismatches[:5]:
            print(f"→ {key}: green={sku1}, phonetrade={sku2}")
    else:
        print("✅ Alle fælles produkter har identisk SKU")
        
def compare_skus_across_shops(green_variants, phonetrade_variants):
    print("\n🔍 Tjekker at ingen SKU’er optræder i begge shops (medmindre det er samme produkt)...")

    green_sku_map = defaultdict(list)
    for v in green_variants:
        if v["sku"]:
            green_sku_map[v["sku"]].append(v["composite_key"])

    phonetrade_sku_map = defaultdict(list)
    for v in phonetrade_variants:
        if v["sku"]:
            phonetrade_sku_map[v["sku"]].append(v["composite_key"])

    shared_skus = set(green_sku_map.keys()) & set(phonetrade_sku_map.keys())

    violations = []
    for sku in shared_skus:
        green_keys = set(green_sku_map[sku])
        phonetrade_keys = set(phonetrade_sku_map[sku])
        if not green_keys & phonetrade_keys:
            violations.append({
                "sku": sku,
                "green_composite_keys": list(green_keys),
                "phonetrade_composite_keys": list(phonetrade_keys),
            })

    if violations:
        print(f"❌ {len(violations)} SKU’er findes i begge shops med forskellige produkter:")
        for v in violations[:5]:
            print(f"→ SKU: {v['sku']}")
            print(f"   Green keys: {v['green_composite_keys']}")
            print(f"   Phonetrade keys: {v['phonetrade_composite_keys']}")
    else:
        print("✅ Ingen SKU-konflikter på tværs af shops")


def main():
    green_variants = get_variants_from_store("green")
    phonetrade_variants = get_variants_from_store("phonetrade")

    check_uniqueness(green_variants, "green")
    check_uniqueness(phonetrade_variants, "phonetrade")

    compare_composite_keys(green_variants, phonetrade_variants)
    compare_skus_across_shops(green_variants, phonetrade_variants)

if __name__ == "__main__":
    main()
