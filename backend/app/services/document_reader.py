"""
Document Reader Service
Reads medical records from the medical records directory
"""
from pathlib import Path
from typing import List, Dict
from app.config import config


class DocumentReader:
    """Service to read medical records from files"""
    
    def __init__(self):
        self.records_dir = config.MEDICAL_RECORDS_DIR
    
    def read_all_records(self) -> str:
        """
        Read all medical record files and return combined text
        
        Returns:
            str: Combined text from all medical records
        """
        if not self.records_dir.exists():
            return ""
        
        all_text = []
        
        # Read all .txt files in the directory
        txt_files = sorted(self.records_dir.glob("*.txt"))
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # Add file name as header
                        all_text.append(f"\n\n=== {file_path.name} ===\n\n")
                        all_text.append(content)
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue
        
        return "\n".join(all_text)
    
    def get_records_list(self) -> List[Dict[str, str]]:
        """
        Get list of all medical records with metadata
        
        Returns:
            List[Dict]: List of records with name and content
        """
        if not self.records_dir.exists():
            return []
        
        records = []
        txt_files = sorted(self.records_dir.glob("*.txt"))
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        records.append({
                            "name": file_path.name,
                            "content": content
                        })
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue
        
        return records
    
    def get_records_with_metadata(self) -> List[Dict]:
        """
        Get list of all medical records with enhanced metadata for RAG
        
        Returns:
            List[Dict]: List of records with name, content, and metadata
        """
        if not self.records_dir.exists():
            return []
        
        records = []
        txt_files = sorted(self.records_dir.glob("*.txt"))
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # Extract date from filename if possible (format: name_YYYY-MM-DD.txt)
                        filename_parts = file_path.stem.split('_')
                        date = None
                        if len(filename_parts) > 1:
                            # Try to parse date from last part
                            try:
                                from datetime import datetime
                                date_str = filename_parts[-1]
                                date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                            except:
                                pass
                        
                        records.append({
                            "name": file_path.name,
                            "source_file": file_path.name,
                            "content": content,
                            "metadata": {
                                "filename": file_path.name,
                                "date": date,
                                "file_type": "medical_record"
                            }
                        })
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue
        
        return records
