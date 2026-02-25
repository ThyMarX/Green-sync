import csv

GREEN_FILE = 'green_products_with_sku.csv'
PHONETRADE_FILE = 'phonetrade_products.csv'
OUTPUT_FILE = 'phonetrade_products_with_updated_sku.csv'
LOG_FILE = 'merge_log.csv'
UNIQUE_LOG_FILE = 'unikke_produkter_log.csv'

def create_composite_key(product_name, variant_name):
    return (product_name + variant_name).lower().replace(" ", "")

def load_products(filepath):
    products = {}
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = create_composite_key(row['Produktnavn'], row['Variantnavn'])
            products[key] = row
    return products

def merge_skus():
    print("🔄 Sammenligner produkter...")

    green_products = load_products(GREEN_FILE)
    phonetrade_products = load_products(PHONETRADE_FILE)

    phonetrade_rows = []
    log_rows = []
    unique_rows = []

    updated_count = 0
    no_match_count = 0
    already_identical = 0

    # Find unikke produkter
    green_keys = set(green_products.keys())
    phonetrade_keys = set(phonetrade_products.keys())

    kun_i_green = green_keys - phonetrade_keys
    kun_i_phonetrade = phonetrade_keys - green_keys

    for key in kun_i_green:
        row = green_products[key]
        unique_rows.append({
            'Produktnavn': row['Produktnavn'],
            'Variantnavn': row['Variantnavn'],
            'Butik': 'Green'
        })

    for key in kun_i_phonetrade:
        row = phonetrade_products[key]
        unique_rows.append({
            'Produktnavn': row['Produktnavn'],
            'Variantnavn': row['Variantnavn'],
            'Butik': 'Phonetrade'
        })

    # Match og opdater SKU'er
    with open(PHONETRADE_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames  # behold original struktur

        for row in reader:
            key = create_composite_key(row['Produktnavn'], row['Variantnavn'])
            phonetrade_sku = row['SKU']

            if key in green_products:
                green_sku = green_products[key]['SKU']
                if green_sku != phonetrade_sku:
                    log_rows.append({
                        'Composite Key': key,
                        'Original SKU': phonetrade_sku,
                        'Updated SKU': green_sku,
                        'Status': 'Opdateret'
                    })
                    row['SKU'] = green_sku
                    updated_count += 1
                else:
                    log_rows.append({
                        'Composite Key': key,
                        'Original SKU': phonetrade_sku,
                        'Updated SKU': phonetrade_sku,
                        'Status': 'Allerede ens'
                    })
                    already_identical += 1
            else:
                log_rows.append({
                    'Composite Key': key,
                    'Original SKU': phonetrade_sku,
                    'Updated SKU': '',
                    'Status': 'Ingen match i Green'
                })
                no_match_count += 1

            phonetrade_rows.append(row)

    # Gem opdateret phonetrade CSV (klar til Shopify-opdatering)
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(phonetrade_rows)

    # Gem log for ændringer
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as log_out:
        writer = csv.DictWriter(log_out, fieldnames=['Composite Key', 'Original SKU', 'Updated SKU', 'Status'])
        writer.writeheader()
        writer.writerows(log_rows)

    # Gem unikke produkter
    with open(UNIQUE_LOG_FILE, 'w', newline='', encoding='utf-8') as unique_out:
        writer = csv.DictWriter(unique_out, fieldnames=['Produktnavn', 'Variantnavn', 'Butik'])
        writer.writeheader()
        writer.writerows(unique_rows)

    print("✅ Merge færdig!")
    print(f"🔢 Opdaterede SKU'er: {updated_count}")
    print(f"✅ Allerede ens SKU'er: {already_identical}")
    print(f"❌ Uden match i Green: {no_match_count}")
    print(f"📄 Gemte opdateret CSV: {OUTPUT_FILE}")
    print(f"📝 Log-fil: {LOG_FILE}")
    print(f"📌 Unikke produkter log: {UNIQUE_LOG_FILE}")

if __name__ == '__main__':
    merge_skus()
