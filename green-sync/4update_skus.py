import csv
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_ADMIN_API_VERSION = os.getenv("SHOPIFY_ADMIN_API_VERSION")

def load_original_skus(original_csv_path):
    variant_sku_map = {}
    with open(original_csv_path, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            variant_id = row.get("Variant ID", "").strip()
            sku = row.get("SKU", "").strip()
            if variant_id:
                variant_sku_map[variant_id] = sku
    return variant_sku_map

def update_variant_sku(shop_domain, api_token, variant_id, new_sku, dry_run):
    try: ###
        variant_id_int = int(variant_id)
    except ValueError:
        return {
            "status": "error",
            "variant_id": variant_id,
            "sku": new_sku,
            "message": "Invalid variant_id – not a number",
            "error": "ValueError"
        }

    if not new_sku: ###
        return {
            "status": "error",
            "variant_id": variant_id,
            "sku": new_sku,
            "message": "Missing new SKU",
            "error": "Empty SKU"
        }

    url = f"https://{shop_domain}/admin/api/{SHOPIFY_ADMIN_API_VERSION}/variants/{variant_id_int}.json"
    headers = {
        "X-Shopify-Access-Token": api_token,
        "Content-Type": "application/json",
    }
    payload = {
        "variant": {
            "id": int(variant_id),
            "sku": new_sku
        }
    }

    if dry_run:
        return {"status": "dry_run", "variant_id": variant_id, "sku": new_sku, "message": "Dry run – no change", "error": ""}

    response = requests.put(url, headers=headers, json=payload)
    if response.status_code == 200:
        time.sleep(0.5)
        return {"status": "updated", "variant_id": variant_id, "sku": new_sku, "message": "SKU updated", "error": ""}
    else:
        return {"status": "error", "variant_id": variant_id, "sku": new_sku, "message": "Update failed", "error": response.text}
    

### Main funktion
def update_skus(shop_key: str, dry_run: bool = True):
    update_count = 0 ### Maks loops 
    max_loops = 0 ### Max loops

    domain_env = f"SHOPIFY_STORE_DOMAIN_{shop_key.upper()}"
    token_env = f"SHOPIFY_ADMIN_API_TOKEN_{shop_key.upper()}"

    store_domain = os.getenv(domain_env)
    api_token = os.getenv(token_env)

    if not store_domain or not api_token:
        print(f"❌ Mangler API-adgang for butik '{shop_key}' i .env")
        return

    updated_csv_path = f"{shop_key.lower()}_products_with_sku.csv"
    original_csv_path = f"{shop_key.lower()}_products.csv"
    output_log_path = f"{shop_key.lower()}_sku_update_log.csv"

    if not os.path.exists(updated_csv_path) or not os.path.exists(original_csv_path):
        print(f"❌ Mangler en eller begge CSV-filer: '{updated_csv_path}' eller '{original_csv_path}'")
        return

    original_skus = load_original_skus(original_csv_path)

    updated = 0
    skipped = 0
    failed = 0
    log_rows = []

    with open(updated_csv_path, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if update_count >= max_loops and max_loops != 0: #Maks loops 
                break

            variant_id = row.get("Variant ID", "").strip()
            new_sku = row.get("SKU", "").strip()
            current_sku = original_skus.get(variant_id, "").strip()

            if not variant_id or not new_sku:
                skipped += 1
                continue

            if current_sku == new_sku:
                skipped += 1
                continue

            if not variant_id.isdigit(): ###
                print(f"❌ Variant ID '{variant_id}' er ikke et gyldigt tal. Skipper.")
                skipped += 1
                continue

            ### variant_exists(store_domain, api_token, variant_id) ### Test funktion

            result = update_variant_sku(store_domain, api_token, variant_id, new_sku, dry_run)

            update_count += 1 ### Maks loops 

            log_rows.append(result)
            if result["status"] == "updated":
                updated += 1
            elif result["status"] == "dry_run":
                pass  # don't count dry_run as updated
            else:
                failed += 1

    with open(output_log_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["status", "variant_id", "sku", "message", "error"])
        writer.writeheader()
        writer.writerows(log_rows)

    print(f"\n📦 SKU-opdatering færdig for butik: {shop_key}")
    print(f"→ Opdateret: {updated}")
    print(f"→ Skippet (allerede korrekt eller mangler data): {skipped}")
    print(f"→ Fejl: {failed}")
    print(f"→ Dry run: {dry_run}")
    print(f"→ Log gemt i: {output_log_path}")

if __name__ == "__main__":
    # Eksempel: Kør med butik "green" eller "phonetrade"
    update_skus("phonetrade", dry_run=False)
