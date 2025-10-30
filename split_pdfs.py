import os
import fitz  # PyMuPDF

# Define the folder path
folder_path = r"[REDACTED_FILE_PATH]"

# Initialize a counter for naming the output PDFs
pdf_counter = 1

# Iterate over all PDF files in the folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".pdf"):
        file_path = os.path.join(folder_path, filename)
        
        # Open the PDF file
        doc = fitz.open(file_path)
        
        # Split each page into a new PDF
        for page_num in range(len(doc)):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            
            # Define the output file name and path
            output_filename = f"pdf {pdf_counter}.pdf"
            output_path = os.path.join(folder_path, output_filename)
            
            # Save the new PDF
            new_doc.save(output_path)
            new_doc.close()
            pdf_counter += 1

        doc.close()

print("PDFs have been successfully split and saved.")