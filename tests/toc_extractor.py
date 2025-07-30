import pypdf
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Google Generative AI model
model = ChatGoogleGenerativeAI(
    model = "gemini-2.0-flash",
    temperature = 0.5,
) # Set more config here or maybe in separate file

class Chapter(BaseModel):
    """Represents a chapter in the table of contents"""
    chapter: int = Field(..., description="Chapter number")
    title: str = Field(..., description="Chapter title")
    page_number: Optional[int] = Field(None, description="Page number where this chapter starts")
    sections: List[str] = Field(..., description="List of sections within the chapter")
    summary: str = Field(..., description="Brief summary of the chapter content")

class TableOfContents(BaseModel):
    """Represents the complete table of contents"""
    chapters: List[Chapter] = Field(..., description="List of all chapters")
    is_complete: bool = Field(default=False, description="Whether the TOC extraction is complete")
    textbook_path: str = Field(..., description="Path to the textbook, Do not fill this field")

class TOCExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.parser = PydanticOutputParser(pydantic_object=TableOfContents)
        
        # Load system prompt from file (following your pattern)
        with open("agents/toc_extractor_config.txt", "r") as file:
            system_message = file.read()
        
        self.prompt_template = ChatPromptTemplate.from_template(system_message)

    def extract_text_from_pages(self, start_page: int, end_page: int) -> str:
        """Extract text from a range of pages"""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                for page_num in range(start_page, min(end_page, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def extract_toc(self) -> TableOfContents:
        """Extract table of contents from the PDF"""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                total_pages = len(pdf_reader.pages)
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return TableOfContents(entries=[], is_complete=False)

        current_toc = TableOfContents(chapters=[], is_complete=False)
        page_size = 5

        for start_page in range(0, total_pages, page_size):
            end_page = min(start_page + page_size, total_pages)
            # Extract text from current 3-page chunk
            pages_content = self.extract_text_from_pages(start_page, end_page)
            
            if not pages_content.strip():
                continue

            # Prepare previous TOC for context
            previous_toc_str = ""
            if current_toc.chapters:
                previous_toc_str = "Previous chapters found:\n"
                for chapter in current_toc.chapters[-5:]:  # Only include last 5 chapters for context
                    # Handle both Pydantic objects and dictionaries
                    if hasattr(chapter, 'chapter'):
                        chapter_num = chapter.chapter
                        chapter_title = chapter.title
                        chapter_page = chapter.page_number
                        chapter_summary = chapter.summary
                    else:
                        chapter_num = chapter.get('chapter', 'Unknown')
                        chapter_title = chapter.get('title', 'Unknown')
                        chapter_page = chapter.get('page_number', 'Unknown')
                        chapter_summary = chapter.get('summary', 'Unknown')
                    previous_toc_str += f"- Chapter {chapter_num}: {chapter_title} (p.{chapter_page})\n"
                    previous_toc_str += f"  Summary: {chapter_summary}\n"

            # Prompt the LLM
            try:
                format_instructions = self.parser.get_format_instructions()
                messages = self.prompt_template.format_messages(
                    previous_toc=previous_toc_str,
                    pages_content=pages_content,
                    format_instructions=format_instructions
                )
                
                response = model.invoke(messages)
                new_toc = self.parser.parse(response.content)
                
                # Add new chapters to current TOC
                if new_toc.chapters:
                    current_toc.chapters.extend(new_toc.chapters)
                    print(f"Found {len(new_toc.chapters)} chapters in pages {start_page + 1}-{end_page}")
            
                print(new_toc)
                
                # Check if TOC extraction is complete
                if new_toc.is_complete:
                    current_toc.is_complete = True
                    print("TOC extraction complete!")
                    break
                    
            except Exception as e:
                print(f"Error processing pages {start_page + 1}-{end_page}: {e}")
                break
        current_toc.textbook_path = self.pdf_path
        return current_toc

def main():
    # Example usage
    pdf_path = "/home/prana/prep_notch_src/tests/jesc1ps.pdf"  # Replace with actual PDF path
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    extractor = TOCExtractor(pdf_path)
    toc = extractor.extract_toc()
    
    # Save results (following your pattern)
    with open("outputs/toc2.json", "w") as f:
        json.dump(toc.model_dump(), f, indent=4)
    
    print(f"Extracted {len(toc.chapters)} chapters")
    print(f"TOC complete: {toc.is_complete}")
    
    # Print first few chapters as preview
    print("\nFirst few chapters:")
    for chapter in toc.chapters[:5]:  # Show first 5 chapters
        # Handle both Pydantic objects and dictionaries
        if hasattr(chapter, 'chapter'):
            chapter_num = chapter.chapter
            chapter_title = chapter.title
            chapter_page = chapter.page_number
            chapter_sections = chapter.sections
        else:
            chapter_num = chapter.get('chapter', 'Unknown')
            chapter_title = chapter.get('title', 'Unknown')
            chapter_page = chapter.get('page_number', 'Unknown')
            chapter_sections = chapter.get('sections', [])

if __name__ == "__main__":
    main()
