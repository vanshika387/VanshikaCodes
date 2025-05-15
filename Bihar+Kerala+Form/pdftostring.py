from PyPDF2 import PdfReader
 
# Create a PdfReader object
reader = PdfReader("sample-1.pdf")
 
# Get the number of pages in the PDF
number_of_pages = len(reader.pages)
 
# Extract text from the first page
page = reader.pages[0]
text = page.extract_text()
 
print(f"Number of pages: {number_of_pages}")
print(f"Text on first page: {text}")