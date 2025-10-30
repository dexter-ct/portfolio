import os
from PyPDF2 import PdfReader, PdfWriter

# Source folder
source_folder = r"[REDACTED_FILE_PATH]"

# Destination file
destination_file = r"[REDACTED_FILE_PATH]"

# PDF writer
pdf_writer = PdfWriter()
skipped = []
errors = []

print("[INFO] Starting PDF processing...")

# Loop through PDFs
for filename in os.listdir(source_folder):
    if filename.lower().endswith(".pdf") and filename != "combined.pdf":
        file_path = os.path.join(source_folder, filename)
        try:
            reader = PdfReader(file_path)
            if len(reader.pages) >= 3:
                pdf_writer.add_page(reader.pages[2])
                print(f"[OK] Added page 3 from: {filename}")
            else:
                skipped.append(filename)
                print(f"[SKIP] '{filename}' has less than 3 pages.")
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"[ERROR] Failed to process '{filename}': {e}")

# Save combined PDF
try:
    with open(destination_file, "wb") as f_out:
        pdf_writer.write(f_out)
    print(f"[SUCCESS] Combined PDF saved to: {destination_file}")
except Exception as e:
    print(f"[ERROR] Failed to save combined PDF: {e}")

# Summary
print("\n[SUMMARY]")
if skipped:
    print(f"Skipped {len(skipped)} file(s):")
    for f in skipped:
        print(f"  - {f}")
if errors:
    print(f"Encountered {len(errors)} error(s):")
    for f, msg in errors:
        print(f"  - {f}: {msg}")
if not skipped and not errors:
    print("All files processed successfully.")