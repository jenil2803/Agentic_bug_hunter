"""
CSV utilities for reading input and writing output
"""
import csv
from pathlib import Path
from typing import List, Dict
from common.config import CSV_COLUMNS, OUTPUT_DIR
from common.logger import get_logger

logger = get_logger("csv_utils")


def read_dataset_csv(csv_path: Path) -> List[Dict]:
    """
    Read the input CSV dataset containing code snippets and bug information
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        List of dictionaries containing code snippet data
    """
    data = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        
        logger.info(f"Successfully read {len(data)} records from {csv_path}")
        return data
    
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_path}: {e}")
        raise


def write_output_csv(results: List[Dict], output_filename: str = "output.csv"):
    """
    Write bug detection results to CSV file
    
    Args:
        results: List of dictionaries with keys: ID, Bug Line, Explanation
        output_filename: Name of the output file
    """
    output_path = OUTPUT_DIR / output_filename
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(results)
        
        logger.info(f"Successfully wrote {len(results)} results to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error writing CSV file {output_path}: {e}")
        raise


def validate_result(result: Dict) -> bool:
    """
    Validate that a result dictionary has all required fields
    
    Args:
        result: Dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    return all(key in result for key in CSV_COLUMNS)


def append_result_to_csv(result: Dict, output_path: Path):
    """
    Append a single result to CSV file in real-time
    
    Args:
        result: Dictionary with keys: ID, Bug Line, Explanation
        output_path: Path to the output CSV file
    """
    try:
        # Check if file exists to determine if we need to write header
        file_exists = output_path.exists()
        
        with open(output_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the result
            writer.writerow(result)
        
        logger.debug(f"Appended result for ID {result.get('ID', 'unknown')} to {output_path}")
        
    except Exception as e:
        logger.error(f"Error appending to CSV file {output_path}: {e}")
        raise
