import pdfplumber
import os
from datetime import datetime
from .extractors import TextExtractor, TableExtractor, ImageExtractor

class PDFtoMarkdownConverter:
    """Main converter class"""
    
    def __init__(self, pdf_path, output_path=None):
        self.pdf_path = pdf_path
        self.output_path = output_path or self._generate_output_path(pdf_path)
        self.text_extractor = TextExtractor()
        self.table_extractor = TableExtractor()
        self.image_extractor = ImageExtractor()
        self.markdown_content = []
    
    def _generate_output_path(self, pdf_path):
        """Generate output markdown path from PDF path"""
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        return f"{base_name}.md"
    
    def convert(self):
        """Convert PDF to Markdown"""
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Add metadata
                self._add_metadata(pdf)
                
                # Process each page
                for page_num, page in enumerate(pdf.pages):
                    self._process_page(page, page_num)
            
            # Write to file
            self._write_markdown()
            print(f"✓ Successfully converted to: {self.output_path}")
            return self.output_path
        
        except Exception as e:
            raise Exception(f"Error converting PDF: {str(e)}")
    
    def _add_metadata(self, pdf):
        """Add metadata to markdown"""
        metadata = pdf.metadata
        self.markdown_content.append("---")
        self.markdown_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.markdown_content.append(f"Total Pages: {len(pdf.pages)}")
        if metadata and metadata.get('Title'):
            self.markdown_content.append(f"Title: {metadata.get('Title')}")
        self.markdown_content.append("---")
        self.markdown_content.append("")
    
    def _process_page(self, page, page_num):
        """Process a single PDF page"""
        # Add page marker
        self.markdown_content.append(f"## Page {page_num + 1}")
        self.markdown_content.append("")
        
        # Extract and format text
        text = self.text_extractor.extract_text(page)
        if text:
            formatted_text = self.text_extractor.format_text(text, page_num)
            self.markdown_content.append(formatted_text)
            self.markdown_content.append("")
        
        # Extract tables
        tables = self.table_extractor.format_tables_in_text(page)
        if tables:
            self.markdown_content.append("### Tables")
            for table in tables:
                self.markdown_content.append(table)
                self.markdown_content.append("")
        
        # Extract images
        images = self.image_extractor.extract_images(page, page_num)
        if images:
            self.markdown_content.append("### Images")
            for image_info in images:
                img_ref = self.image_extractor.get_markdown_image_reference(image_info)
                self.markdown_content.append(img_ref)
            self.markdown_content.append("")
    
    def _write_markdown(self):
        """Write markdown content to file"""
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.markdown_content))