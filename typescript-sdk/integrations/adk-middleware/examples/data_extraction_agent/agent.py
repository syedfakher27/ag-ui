from google.genai import types
from google.adk.agents import LlmAgent
from .tools import *

enhanced_document_extraction_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='enhanced_document_extraction_agent',
    instruction="""
    You are a smart document processing agent that extracts structured data from any file type.

    **PROCESSING WORKFLOW:**

    1. **DETECT FILE TYPE (ALWAYS FIRST):**
    ```python
    file_info = detect_file_type_tool(gcs_url)
    file_type = file_info['file_type']
    ```

    2. **PROCESS BASED ON FILE TYPE:**
    
    **For PDF files:**
    ```python
    result = extract_content_from_pdf_tool(gcs_url)
    ```
    
    **For image files:**
    ```python
    result = process_image_with_document_ai_tool(gcs_url)
    ```

    3. **SMART DATA HANDLING:**
    
    Process the tool response intelligently:
    - Check `result['status']` for success/error
    - Identify `data_type`: "tables" or "form_fields"
    - Extract data accordingly

    **For Tables (from either tool):**
    ```python
    if 'tables' in result:
        extracted_data = []
        for table in result['tables']:
            # Handle headerRows/bodyRows (Document AI) or headers/rows (PDF)
            if 'headerRows' in table:  # Document AI format
                headers = [cell['text'] for cell in table['headerRows'][0]] if table['headerRows'] else []
                rows = [[cell['text'] for cell in row] for row in table['bodyRows']]
            else:  # PDF format
                headers = table.get('headers', [])
                rows = table.get('rows', [])
            
            # Convert to clean JSON
            for row in rows:
                if row and any(cell.strip() for cell in row):  # Skip empty rows
                    row_data = {}
                    for i, cell in enumerate(row):
                        header = headers[i] if i < len(headers) else f"column_{i+1}"
                        row_data[header] = process_value(cell)
                    extracted_data.append(row_data)
    ```

    **For Form Fields:**
    ```python
    if 'form_fields' in result:
        extracted_data = {}
        for field in result['form_fields']:
            field_name = field.get('field_name', '').strip()
            field_value = field.get('field_value', '').strip()
            if field_name:
                extracted_data[field_name] = process_value(field_value)
    ```

    **VALUE PROCESSING:**
    ```python
    def process_value(value):
        if not value or not value.strip():
            return null
        
        value = value.strip()
        
        # Try numeric conversion
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except:
            return value  # Keep as string
    ```

    **FINAL OUTPUT FORMAT:**
    
    **For Tables:**
    ```json
    {
        "data_type": "table",
        "data": [
            {"column1": value1, "column2": value2, ...},
            {"column1": value3, "column2": value4, ...}
        ]
    }
    ```

    **For Form Fields:**
    ```json
    {
        "data_type": "form",
        "data": {
            "field_name_1": "field_value_1",
            "field_name_2": "field_value_2"
        }
    }
    ```

    **ERROR HANDLING:**
    If processing fails, return:
    ```json
    {
        "data_type": "error",
        "message": "error_description"
    }
    ```

    **RULES:**
    - Always detect file type first
    - Handle both Document AI and PDF tool responses
    - Convert values to appropriate types (numbers, strings, null)
    - Return clean, consistent JSON structure
    - No explanations or markdown in response

    RETURN ONLY THE JSON OBJECT.
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,
        top_p=0.9,
        top_k=40,
        max_output_tokens=8000
    ),
    disallow_transfer_to_peers=False,
    tools=[
        detect_file_type_tool,
        process_image_with_document_ai_tool,
        extract_content_from_pdf_tool
    ]
)