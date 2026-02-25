import csv
import os

INPUT_FILE = "green_products.csv"
OUTPUT_FILE = "green_products_with_sku.csv"
SKU_PREFIX = "AUTOSKU-"
SKU_LENGTH = 8  # fx: AUTOSKU-00000A1Z

BASE36_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def int_to_base36(num):
    if num < 0:
        raise ValueError("Negative SKU index not allowed.")
    chars = []
    while num > 0:
        num, rem = divmod(num, 36)
        chars.append(BASE36_CHARS[rem])
    return ''.join(reversed(chars)).rjust(SKU_LENGTH, '0')

def generate_new_sku(index):
    return f"{SKU_PREFIX}{int_to_base36(index)}"

def update_skus():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Inputfilen '{INPUT_FILE}' blev ikke fundet.")
        return

    with open(INPUT_FILE, mode="r", newline="", encoding="utf-8") as infile:
        reader = list(csv.DictReader(infile))
        fieldnames = reader[0].keys()

        seen_skus = set()
        duplicate_skus = set()
        missing_sku_rows = []
        total_rows = len(reader)

        for row in reader:
            sku = row.get("SKU", "").strip()
            if not sku:
                missing_sku_rows.append(row)
            elif sku in seen_skus:
                duplicate_skus.add(sku)
                print(f"📦 Duplet Sku: {sku}") ## New!
                missing_sku_rows.append(row)
            else:
                seen_skus.add(sku)

        next_sku_index = 1
        used_skus = set(seen_skus)
        newly_generated = 0
        for row in missing_sku_rows:
            while True:
                new_sku = generate_new_sku(next_sku_index)
                next_sku_index += 1
                if new_sku not in used_skus:
                    used_skus.add(new_sku)
                    break
            row["SKU"] = new_sku
            newly_generated += 1

        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                writer.writerow(row)

    # Valider at alle SKU'er nu er unikke og ikke-tomme
    with open(OUTPUT_FILE, mode="r", newline="", encoding="utf-8") as checkfile:
        checkreader = csv.DictReader(checkfile)
        all_skus = [row["SKU"].strip() for row in checkreader]

    unique_skus = set(all_skus)
    empty_skus = [sku for sku in all_skus if not sku]

    print("\n🔍 STATUSRAPPORT:")
    print(f"📦 Antal rækker i alt: {total_rows}")
    print(f"❌ Tomme SKU'er før opdatering: {len([r for r in reader if not r['SKU'].strip()])}")
    print(f"⚠️ Duplet SKU'er før opdatering: {len(duplicate_skus)}")
    print(f"🔧 Antal SKU'er der blev genereret/opdateret: {newly_generated}")
    print(f"✅ Unikke SKU'er efter opdatering: {len(unique_skus)}")
    print(f"🚫 Tomme SKU'er efter opdatering: {len(empty_skus)}")

    if len(unique_skus) == total_rows and len(empty_skus) == 0:
        print("🎉 Alle SKU’er er nu unikke og gyldige.")
    else:
        print("⚠️ FEJL: Der er stadig tomme eller duplikerede SKU’er. Tjek outputfilen manuelt.")

if __name__ == "__main__":
    update_skus()
