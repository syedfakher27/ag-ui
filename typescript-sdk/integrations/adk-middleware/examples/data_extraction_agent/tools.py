from typing import Dict, Any
from google.cloud import storage
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
import os

project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', "slamsportsai")
processor_id = os.environ.get('PROCESSOR_ID', "c969f4760002c946")
location = "us"

def process_image_with_document_ai_tool(gcs_url: str) -> Dict[str, Any]:
    """
    Process images using Google Cloud Document AI Form Processor to extract table data and form fields.
    
    Args:
        gcs_url: GCS URL of the image to process
        project_id: Google Cloud project ID
        location: Document AI location
        processor_id: Document AI processor ID
        
    Returns:
        Dictionary containing extracted table data and/or form fields
    """
    print("Starting Document AI processing for image...")
    
    try:
        # Parse GCS URL
        if not gcs_url.startswith('gs://'):
            return {
                "status": "error",
                "message": f"Invalid GCS URL format: {gcs_url}"
            }
        
        path_parts = gcs_url[5:].split("/", 1)
        bucket_name = path_parts[0]
        blob_path = path_parts[1]
        
        print(f"Creating Document AI client...")
        # Create Document AI client
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        print("Client created successfully")
        
        # Get processor path
        processor_name = client.processor_path(project_id, location, processor_id)
        print(f"Processor path: {processor_name}")
        
        # Download image from GCS
        print(f"Reading image from GCS...")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        if not blob.exists():
            return {
                "status": "error",
                "message": f"Image not found at: {gcs_url}"
            }
        
        image_content = blob.download_as_bytes()
        print(f"Image downloaded successfully. Size: {len(image_content)} bytes")
        
        # Determine MIME type
        mime_type = "image/png"  # Default
        if gcs_url.lower().endswith(('.jpg', '.jpeg')):
            mime_type = "image/jpeg"
        elif gcs_url.lower().endswith('.gif'):
            mime_type = "image/gif"
        elif gcs_url.lower().endswith('.bmp'):
            mime_type = "image/bmp"
        
        print(f"Creating RawDocument with MIME type: {mime_type}")
        # Create Document AI request
        raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=processor_name, raw_document=raw_document)
        
        # Process document
        print("Processing document with Document AI...")
        result = client.process_document(request=request)
        document = result.document
        print(f"Document processed successfully. Pages: {len(document.pages)}")
        
        # Initialize response data
        response_data = {
            "status": "success",
            "method": "document_ai",
            "full_text": document.text,
            "processing_summary": {
                "pages_processed": len(document.pages),
                "extraction_method": "Google Cloud Document AI Form Processor"
            }
        }
        
        # Extract tables first
        print("Checking for tables in processed document...")
        tables_data = []
        total_tables = 0
        
        for page_idx, page in enumerate(document.pages):
            print(f"Processing page {page_idx + 1}")
            page_tables = len(page.tables)
            total_tables += page_tables
            print(f" Found {page_tables} table(s) on page {page_idx + 1}")
            
            for table_idx, table in enumerate(page.tables):
                print(f" Processing table {table_idx + 1}")
                
                # Extract header rows
                header_rows = []
                for row_idx, header_row in enumerate(table.header_rows):
                    header_cells = []
                    for cell in header_row.cells:
                        cell_text = get_text_from_layout(cell.layout, document.text)
                        header_cells.append({
                            "text": cell_text.strip(),
                            "rowSpan": getattr(cell, 'row_span', 1),
                            "colSpan": getattr(cell, 'col_span', 1)
                        })
                    header_rows.append(header_cells)
                    print(f"Header row {row_idx + 1}: {len(header_cells)} cells")
                
                # Extract body rows
                body_rows = []
                for row_idx, body_row in enumerate(table.body_rows):
                    body_cells = []
                    for cell in body_row.cells:
                        cell_text = get_text_from_layout(cell.layout, document.text)
                        body_cells.append({
                            "text": cell_text.strip(),
                            "rowSpan": getattr(cell, 'row_span', 1),
                            "colSpan": getattr(cell, 'col_span', 1)
                        })
                    body_rows.append(body_cells)
                    if (row_idx + 1) % 10 == 0:
                        print(f"Processed {row_idx + 1} body rows...")
                
                table_data = {
                    "headerRows": header_rows,
                    "bodyRows": body_rows,
                    "table_index": f"page_{page_idx + 1}_table_{table_idx + 1}"
                }
                tables_data.append(table_data)
                print(f"Table {table_idx + 1} extraction complete")
        
        if total_tables > 0:
            print(f"Found {total_tables} table(s)! Using table extraction mode.")
            response_data.update({
                "data_type": "tables",
                "tables_found": len(tables_data),
                "tables": tables_data,
                "processing_summary": {
                    **response_data["processing_summary"],
                    "total_tables": total_tables
                }
            })
        else:
            print(" No tables found. Extracting form fields...")
            # Extract form fields
            form_fields = []
            total_form_fields = 0
            
            for page_idx, page in enumerate(document.pages):
                print(f"Processing form fields on page {page_idx + 1}")
                page_form_fields = len(page.form_fields)
                total_form_fields += page_form_fields
                print(f"Found {page_form_fields} form field(s) on page {page_idx + 1}")
                
                for field_idx, field in enumerate(page.form_fields):
                    print(f"Processing form field {field_idx + 1}")
                    
                    # Extract field name
                    field_name = ""
                    if field.field_name and field.field_name.text_anchor:
                        field_name = get_text_from_layout(field.field_name, document.text).strip()
                    
                    # Extract field value
                    field_value = ""
                    if field.field_value and field.field_value.text_anchor:
                        field_value = get_text_from_layout(field.field_value, document.text).strip()
                    
                    # Get confidence scores
                    name_confidence = getattr(field.field_name, 'confidence', 0.0) if field.field_name else 0.0
                    value_confidence = getattr(field.field_value, 'confidence', 0.0) if field.field_value else 0.0
                    
                    # Get bounding boxes if available
                    name_bbox = None
                    value_bbox = None
                    
                    if field.field_name and hasattr(field.field_name, 'bounding_poly'):
                        name_bbox = field.field_name.bounding_poly
                    
                    if field.field_value and hasattr(field.field_value, 'bounding_poly'):
                        value_bbox = field.field_value.bounding_poly
                    
                    form_field_data = {
                        "field_name": field_name,
                        "field_value": field_value,
                        "name_confidence": name_confidence,
                        "value_confidence": value_confidence,
                        "field_index": f"page_{page_idx + 1}_field_{field_idx + 1}",
                        "bounding_boxes": {
                            "name_bbox": name_bbox,
                            "value_bbox": value_bbox
                        }
                    }
                    form_fields.append(form_field_data)
                    print(f"       Field: '{field_name}' = '{field_value}' (conf: {name_confidence:.2f}, {value_confidence:.2f})")
            
            print(f"Form field extraction complete! Total fields: {total_form_fields}")
            response_data.update({
                "data_type": "form_fields",
                "form_fields_found": len(form_fields),
                "form_fields": form_fields,
                "processing_summary": {
                    **response_data["processing_summary"],
                    "total_form_fields": total_form_fields
                }
            })
        
        print(f"Document AI processing completed!")
        return response_data
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Document AI processing failed: {str(e)}",
            "error_type": "document_ai_error"
        }

def get_text_from_layout(layout, full_text: str) -> str:
    """Extract text from a layout object using text segments."""
    if not layout.text_anchor or not layout.text_anchor.text_segments:
        return ""
    
    text = ""
    for segment in layout.text_anchor.text_segments:
        start_index = int(segment.start_index) if segment.start_index else 0
        end_index = int(segment.end_index) if segment.end_index else len(full_text)
        text += full_text[start_index:end_index]
    return text

# PDF Content Extraction Tool
def extract_content_from_pdf_tool(gcs_url: str) -> Dict[str, Any]:
    """
    Extract raw content from PDF files for agent processing.
    Returns tables and text content without pre-processing into specific structures.
    
    Args:
        gcs_url: GCS URL of the PDF file
        
    Returns:
        Dictionary containing raw extracted tables and text content
    """
    print("Starting PDF content extraction...")
    print(f"   PDF URL: {gcs_url}")
 
    from typing import Optional
    import PyPDF2
    import io
    import tempfile
    import os
    from google.cloud import storage
    from urllib.parse import urlparse
    
    # Parse GCS URL
    if not gcs_url.startswith('gs://'):
        return {
            "status": "error",
            "message": f"Invalid GCS URL format: {gcs_url}"
        }
    
    path_parts = gcs_url[5:].split("/", 1)
    bucket_name = path_parts[0]
    blob_path = path_parts[1]
    
    print(f"Downloading PDF from GCS...")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    
    if not blob.exists():
        return {
            "status": "error",
            "message": f"PDF not found at: {gcs_url}"
        }
    
    pdf_content = blob.download_as_bytes()
    print(f"PDF downloaded. Size: {len(pdf_content)} bytes")
    
    temp_file_path = None
    try:
        # Try pdfplumber first for better table detection
        try:
            import pdfplumber
            print("Using pdfplumber for table extraction...")
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            extracted_tables = []
            full_text = ""
            
            with pdfplumber.open(temp_file_path) as pdf:
                print(f"Processing {len(pdf.pages)} page(s)...")
                
                for page_num, page in enumerate(pdf.pages):
                    print(f"Processing page {page_num + 1}")
                    
                    # Extract page text
                    page_text = page.extract_text()
                    if page_text:
                        full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                    
                    # Extract raw tables from page
                    tables = page.extract_tables()
                    print(f"Found {len(tables)} table(s) on page {page_num + 1}")
                    
                    # Only process if tables are found
                    if tables:
                        for table_idx, table in enumerate(tables):
                            if table and len(table) > 0:
                                print(f"Extracting table {table_idx + 1} with {len(table)} rows")
                                
                                # Clean table data but don't assume header structure
                                cleaned_table = []
                                for row_idx, row in enumerate(table):
                                    if row:
                                        # Clean each cell but preserve original content
                                        cleaned_row = []
                                        for cell in row:
                                            if cell is not None:
                                                cleaned_cell = str(cell).strip()
                                                cleaned_row.append(cleaned_cell if cleaned_cell else None)
                                            else:
                                                cleaned_row.append(None)
                                        
                                        # Include row if it has any content
                                        if any(cell for cell in cleaned_row):
                                            cleaned_table.append(cleaned_row)
                                
                                if cleaned_table:
                                    table_dict = {
                                        'table_index': f"page_{page_num + 1}_table_{table_idx + 1}",
                                        'page_number': page_num + 1,
                                        'table_number': table_idx + 1,
                                        'raw_data': cleaned_table,
                                        'row_count': len(cleaned_table),
                                        'column_count': len(cleaned_table[0]) if cleaned_table else 0
                                    }
                                    extracted_tables.append(table_dict)
                                    print(f"Added table with {len(cleaned_table)} rows and {len(cleaned_table[0]) if cleaned_table else 0} columns")
                    else:
                        print(f"No tables found on page {page_num + 1}, continuing with text extraction only")
            
            print(f"PDF processing completed! Found {len(extracted_tables)} table(s)")
            
            return {
                'status': 'success',
                'method': 'pdfplumber',
                'tables_found': len(extracted_tables),
                'tables': extracted_tables,
                'full_text': full_text.strip(),
                'content_summary': {
                    'pages_processed': len(pdf.pages),
                    'tables_extracted': len(extracted_tables),
                    'total_text_length': len(full_text.strip())
                }
            }
            
        except ImportError:
            print("pdfplumber not available, falling back to PyPDF2")
        
        # Fallback to PyPDF2 for text-only extraction
        print("Using PyPDF2 for text extraction...")
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        full_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text.strip():
                full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        return {
            'status': 'success',
            'method': 'pypdf2',
            'tables_found': 0,
            'tables': [],
            'full_text': full_text.strip(),
            'content_summary': {
                'pages_processed': len(pdf_reader.pages),
                'tables_extracted': 0,
                'total_text_length': len(full_text.strip()),
                'note': 'Only text extraction available with PyPDF2'
            }
        }
                
    except Exception as e:
        return {
            'status': 'error',
            'message': f"PDF extraction failed: {str(e)}",
            'error_type': 'pdf_extraction_error'
        }
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
# File Type Detection Tool
def detect_file_type_tool(gcs_url: str) -> Dict[str, Any]:
    """
    Detect file type from GCS URL and recommend appropriate extraction method.
    
    Args:
        gcs_url: GCS URL to analyze
        
    Returns:
        Dictionary with file type and processing recommendations
    """
    print(f"🔍 Detecting file type for: {gcs_url}")
    
    url_lower = gcs_url.lower()
    
    if url_lower.endswith('.pdf') or 'pdf' in url_lower:
        file_type = 'pdf'
        recommended_tool = 'extract_text_from_pdf_tool'
    elif any(ext in url_lower for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff']):
        file_type = 'image'
        recommended_tool = 'process_image_with_document_ai_tool'
    else:
        file_type = 'unknown'
        recommended_tool = 'process_image_with_document_ai_tool'  # Default to image processing
    
    print(f"Detected file type: {file_type}")
    
    return {
        "status": "success",
        "file_type": file_type,
        "gcs_url": gcs_url,
        "recommended_tool": recommended_tool,
        "processing_strategy": {
            "pdf": "Use extract_text_from_pdf_tool for table detection and text extraction",
            "image": "Use process_image_with_document_ai_tool for precise table structure extraction",
            "unknown": "Default to image processing with Document AI"
        }[file_type],
        "next_steps": f"Call {recommended_tool}('{gcs_url}') to extract data"
    }