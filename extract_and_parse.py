import fitz  # PyMuPDF
import re
import yaml
from collections import defaultdict

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Function to parse the extracted text
def parse_text(text):
    control_families = {}
    control_metadata = {}
    control_text = {}

    # Regex patterns to match the control families, metadata, and text
    family_pattern = re.compile(r"(Family:)\s*(.*)")
    control_pattern = re.compile(r"(Control:)\s*(.*)")
    enhancement_pattern = re.compile(r"(Enhancement:)\s*(.*)")
    guidance_pattern = re.compile(r"(Guidance:)\s*(.*)")

    lines = text.split('\n')
    current_family = None
    current_control = None

    for line in lines:
        family_match = family_pattern.match(line)
        control_match = control_pattern.match(line)
        enhancement_match = enhancement_pattern.match(line)
        guidance_match = guidance_pattern.match(line)

        if family_match:
            current_family = family_match.group(2).strip()
            control_families[current_family] = {"family": current_family}
        elif control_match:
            current_control = control_match.group(2).strip()
            control_metadata[current_control] = {"id": current_control, "family": current_family}
            control_text[current_control] = {"id": current_control, "text": "", "guidance": ""}
        elif enhancement_match:
            current_control = enhancement_match.group(2).strip()
            control_metadata[current_control] = {"id": current_control, "family": current_family, "enhancement": True}
            control_text[current_control] = {"id": current_control, "text": "", "guidance": ""}
        elif guidance_match:
            if current_control:
                control_text[current_control]["guidance"] += line + "\n"
        elif current_control:
            control_text[current_control]["text"] += line + "\n"

    return control_families, control_metadata, control_text

# Function to save parsed data to YAML files
def save_to_yaml(data, file_name):
    with open(file_name, 'w') as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

# Main script
pdf_path = "NIST.SP.800-53Ar5.pdf"
text = extract_text_from_pdf(pdf_path)
control_families, control_metadata, control_text = parse_text(text)

save_to_yaml(control_families, 'control-families.yaml')
save_to_yaml(control_metadata, 'control-metadata.yaml')
save_to_yaml(control_text, 'control-text.yaml')

print("Extraction and parsing complete. Data saved to YAML files.")
