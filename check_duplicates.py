import pandas as pd
import numpy as np
from datetime import datetime
import re

def get_ticker_from_main():
    with open('main.py', 'r') as file:
        content = file.read()
        # Find the line that defines the ticker
        match = re.search(r'ticker\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    return None

def find_repeated_values(df, filename, output_file):
    with open(output_file, 'w') as f:
        def write_output(text):
            print(text)
            f.write(text + '\n')

        write_output(f"Repeated Values Analysis for {filename}")
        write_output(f"Analysis performed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        write_output("=" * 50 + "\n")

        # Check the date range in the dataframe
        date_column = None
        # Look for a date column (usually named 'Date')
        for col in df.columns:
            if col.lower() == 'date' or 'date' in str(col).lower():
                date_column = col
                break
        
        # Determine if dataset spans more than 3 months
        skip_2x_values = False
        if date_column and pd.api.types.is_datetime64_any_dtype(df[date_column]):
            date_range = df[date_column].max() - df[date_column].min()
            months = date_range.days / 30.44  # Average days per month
            skip_2x_values = months > 3
            write_output(f"Date range spans approximately {months:.1f} months")
            if skip_2x_values:
                write_output("Range exceeds 3 months - 2X repeated values will be excluded")
        
        # Get numeric columns only
        numeric_df = df.select_dtypes(include=[np.number])
        
        # Create a flat list of all values
        all_values = numeric_df.values.flatten()
        
        # Round values to 2 decimal places to avoid floating point issues
        all_values = np.round(all_values, 2)
        
        # Find unique values and their counts
        unique_values, counts = np.unique(all_values, return_counts=True)
        
        # Get repeated values (count > 1)
        if skip_2x_values:
            # Only include values that appear 3 or more times
            repeated_mask = counts > 2
        else:
            # Include all repeated values (appearing 2 or more times)
            repeated_mask = counts > 1
            
        repeated_values = unique_values[repeated_mask]
        repeated_counts = counts[repeated_mask]
        
        if len(repeated_values) > 0:
            write_output("Found the following repeated values:")
            write_output("-" * 50 + "\n")
              # First sort by value (descending)
            value_sort_idx = np.argsort(-repeated_values)
            repeated_values = repeated_values[value_sort_idx]
            repeated_counts = repeated_counts[value_sort_idx]
            
            # Group by count
            count_groups = {}
            for value, count in zip(repeated_values, repeated_counts):
                if count not in count_groups:
                    count_groups[count] = []
                count_groups[count].append(value)
            
            # Display grouped by count, with values sorted from high to low
            for count in sorted(count_groups.keys(), reverse=True):
                write_output(f"\nValues that appear {count} times:")
                write_output("-" * 30)
                for value in sorted(count_groups[count], reverse=True):
                    write_output(f"Level: {value:.2f}")
                write_output("")
        else:
            write_output("No repeated values found in the dataset.")

try:
    # Get ticker symbol from main.py
    ticker = get_ticker_from_main()
    if ticker is None:
        print("Could not find ticker symbol in main.py")
        exit(1)

    # Create the filename based on the ticker symbol
    excel_filename = f'{ticker}_fibonacci_levels.xlsx'
    output_file = f"repeated_values_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    try:
        df = pd.read_excel(excel_filename)
        find_repeated_values(df, excel_filename, output_file)
    except Exception as e:
        print(f"Error processing {excel_filename}: {e}")
        with open(output_file, 'a') as f:
            f.write(f"\nError processing {excel_filename}: {e}\n")

except Exception as e:
    print(f"Error: {e}")