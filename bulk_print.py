import os
from pypdf import PdfReader, PdfWriter

# Define the folder containing the PDFs
pdf_folder = r"[REDACTED_FILE_PATH]"

# Create a PdfWriter object
writer = PdfWriter()

# Get all PDF files in the folder
pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
pdf_files.sort()  # Optional: sort alphabetically

# Add pages from each PDF
for pdf_file in pdf_files:
    pdf_path = os.path.join(pdf_folder, pdf_file)
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        writer.add_page(page)

# Save the combined PDF
output_path = os.path.join(pdf_folder, "combined_output.pdf")
with open(output_path, "wb") as f:
    writer.write(f)

print(f"Combined PDF created successfully: {output_path}")
