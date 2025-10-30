
#!/usr/bin/env python3
import sys
import os
import csv

def txt_to_csv(txt_file):
    base, _ = os.path.splitext(txt_file)
    cleaned_rows = []
    negative_found = False  # Flag for negative values

    with open(txt_file, newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter=',', quotechar='"')
        for row in reader:
            if not row:
                continue
            # Trim padding from every field
            row = [col.strip() for col in row]
            # Keep only columns A–E
            row = row[:5]
            # Ensure column B is a plain 10-digit value with leading zeros
            if len(row) >= 2:
                row[1] = row[1].zfill(10)
            # Check for negative value in column C
            if len(row) >= 3:
                try:
                    if float(row[2]) < 0:
                        negative_found = True
                except ValueError:
                    pass  # Ignore non-numeric values
            cleaned_rows.append(row)

    # Remove rows where column A is missing or empty
    cleaned_rows = [row for row in cleaned_rows if row and row[0]]

    # Adjust filename if negative values were found
    csv_file = base + ("_NEGATIVE.csv" if negative_found else ".csv")

    with open(csv_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(cleaned_rows)

    print(f'Converted: {txt_file} -> {csv_file}')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python allpay.py <input.txt>")
        raise SystemExit(1)
    txt_to_csv(sys.argv[1])
