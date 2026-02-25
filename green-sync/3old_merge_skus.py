# Re-run the merge_sku.py logic after kernel reset

import csv

# Filnavne
GREEN_CSV = "/mnt/data/green_products.csv" ## ÆNDRET
PHONETRADE_CSV = "/mnt/data/phonetrade_products.csv"
PHONETRADE_UPDATED_CSV = "/mnt/data/phonetrade_products_with_updated_sku.csv"
UNIKKE_LOG_CSV = "/mnt/data/unikke_produkter_log.csv"

# Hjælpefunktioner
def load_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_csv(filepath, fieldnames, rows):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def composite_key(row):
    produkt = row.get("Produktnavn", "").lower().replace(" ", "")
    variant = row.get("Variantnavn", "").lower().replace(" ", "")
    return produkt + variant

def generate_sku(index):
    return f"AUTOSKU2-{index:08d}"

# 1. Indlæs data
green_rows = load_csv(GREEN_CSV)
phonetrade_rows = load_csv(PHONETRADE_CSV)

# 2. Byg opslagsdict for green og phonetrade
green_dict = {composite_key(row): row for row in green_rows}
phonetrade_dict = {composite_key(row): row for row in phonetrade_rows}

# 3. Merge og find unikke
updated_phonetrade_rows = []
unikke_produkter = []
sku_index = 1

match_and_updated = 0
already_same = 0
only_in_phonetrade = 0
only_in_green = 0

for row in phonetrade_rows:
    key = composite_key(row)
    if key in green_dict:
        green_sku = green_dict[key].get("SKU", "")
        if row.get("SKU", "") != green_sku:
            row["SKU"] = green_sku
            match_and_updated += 1
        else:
            already_same += 1
    else:
        # Unikt i Phonetrade → tildel nyt SKU
        row["SKU"] = generate_sku(sku_index)
        sku_index += 1
        only_in_phonetrade += 1
        unikke_produkter.append({**row, "Butik": "Phonetrade"})
    updated_phonetrade_rows.append(row)

# Find produkter kun i Green
for row in green_rows:
    key = composite_key(row)
    if key not in phonetrade_dict:
        only_in_green += 1
        unikke_produkter.append({**row, "Butik": "Green"})

# 4. Sortér unikke produkter: butik → produktnavn
unikke_produkter.sort(key=lambda x: (x["Butik"], x.get("Produktnavn", "").lower()))

# 5. Gem filer
save_csv(PHONETRADE_UPDATED_CSV, phonetrade_rows[0].keys(), updated_phonetrade_rows)
save_csv(UNIKKE_LOG_CSV, list(unikke_produkter[0].keys()), unikke_produkter)

# 6. Returner statistik
{
    "SKU opdateret (fra Green)": match_and_updated,
    "SKU allerede ens": already_same,
    "Nye SKU'er genereret (unikke i Phonetrade)": only_in_phonetrade,
    "Produkter kun i Green": only_in_green,
    "Total unikke produkter logget": len(unikke_produkter)
}
