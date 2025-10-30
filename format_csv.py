import pandas as pd
import sys
import os

# Get the file path from the command line argument
file_path = sys.argv[1]

# Load the CSV file with all columns as strings
df = pd.read_csv(file_path, dtype=str)

# Remove 'MP' from 'Payment Reference', preserve leading zeros, and pad to 10 digits
df['Payment Reference'] = df['Payment Reference'].str.replace('MP', '', regex=False).str.zfill(10)

# Add 'MP' as a new column
df['Suffix'] = 'MP'

# Reorder columns
formatted_df = df[['Payment Reference', 'Payment Due', 'AP Start Date', 'AP End Date', 'Amount', 'Suffix']]

# Get the first date from column B ('Payment Due') and format as dd.mm.yy
date_str = pd.to_datetime(formatted_df['Payment Due'].iloc[0], dayfirst=True).strftime('%d.%m.%y')

# Save the formatted DataFrame to a new CSV file in the same folder
output_filename = f"{date_str}.csv"
output_path = os.path.join(os.path.dirname(file_path), output_filename)
formatted_df.to_csv(output_path, index=False, header=False)
