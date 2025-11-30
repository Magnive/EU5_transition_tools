import pandas as pd
import sys
import os

def xlsx_to_csv(xlsx_file, output_dir=None):
    """
    Convert an Excel (.xlsx) file to CSV file(s).
    If the Excel file has multiple sheets, each sheet will be saved as a separate CSV.
    
    Args:
        xlsx_file: Path to the .xlsx file
        output_dir: Optional directory to save CSV files. If None, saves in same directory as xlsx file.
    """
    # Get the base filename without extension
    base_name = os.path.splitext(os.path.basename(xlsx_file))[0]
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.dirname(xlsx_file)
        if not output_dir:
            output_dir = '.'
    
    # Read all sheets from the Excel file
    excel_file = pd.ExcelFile(xlsx_file)
    
    print(f"Converting '{xlsx_file}'...")
    print(f"Found {len(excel_file.sheet_names)} sheet(s): {', '.join(excel_file.sheet_names)}")
    
    # Convert each sheet to CSV
    for sheet_name in excel_file.sheet_names:
        # Read the sheet
        df = pd.read_excel(xlsx_file, sheet_name=sheet_name)
        
        # Create output filename
        if len(excel_file.sheet_names) == 1:
            # If only one sheet, use the base filename
            csv_filename = f"{base_name}.csv"
        else:
            # If multiple sheets, append sheet name
            csv_filename = f"{base_name}_{sheet_name}.csv"
        
        csv_path = os.path.join(output_dir, csv_filename)
        
        # Save to CSV
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"  ? Saved '{sheet_name}' -> '{csv_filename}'")
    
    print(f"\nConversion complete!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python xlsx_to_csv.py <input.xlsx> [output_directory]")
        print("\nExample:")
        print("  python xlsx_to_csv.py data.xlsx")
        print("  python xlsx_to_csv.py data.xlsx output_folder")
        sys.exit(1)
    
    xlsx_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(xlsx_file):
        print(f"Error: File '{xlsx_file}' not found.")
        sys.exit(1)
    
    if not xlsx_file.lower().endswith('.xlsx'):
        print(f"Warning: File '{xlsx_file}' doesn't have .xlsx extension.")
    
    try:
        xlsx_to_csv(xlsx_file, output_dir)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
