import sys
import pandas as pd
import os

# Get the input file path from command-line arguments
if len(sys.argv) < 2:
    print("Usage: python SWIPE.py <path_to_csv>")
    sys.exit(1)

input_csv = sys.argv[1]
filename = os.path.splitext(os.path.basename(input_csv))[0]
input_folder = os.path.dirname(input_csv)
output_csv = os.path.join(input_folder, f"Updated_FORMAT_{filename}.csv")

# Load the CSV with leading zeros preserved
raw_df = pd.read_csv(input_csv, dtype={"Payment Reference": str})

# Function to split address into required parts
def split_address_logic(address):
    parts = [part.strip() for part in str(address).split(',')]
    if len(parts) >= 2:
        postcode = parts[-1]
        second_last = parts[-2]
        main_address = ', '.join(parts[:-2])
    else:
        postcode = parts[-1] if parts else ''
        second_last = ''
        main_address = ''
    return pd.Series([main_address, second_last, postcode])

# Apply the address splitting function to column O (index 14)
address_df = raw_df.iloc[:, 14].apply(split_address_logic)
address_df.columns = ['Address', 'Second Last', 'Postcode']

# Create the formatted DataFrame
formatted_df = pd.DataFrame({
    'Payment Reference': raw_df['Payment Reference'],
    'Name': raw_df['Contact group names'],
    ' ': '',  # Column C (single space)
    'Address': address_df['Address'],
    '  ': '',  # Column E (double space)
    'Second Last': address_df['Second Last'],  # Column F
    'Postcode': address_df['Postcode'],        # Column G
    'Account Type': raw_df['Account Type'].str.upper()  # Column H
})

# Save to CSV in the same folder
formatted_df.to_csv(output_csv, index=False)
print(f"Formatted CSV file saved to: {output_csv}")
