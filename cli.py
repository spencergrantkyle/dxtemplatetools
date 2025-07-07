#!/usr/bin/env python3
"""
Command-line interface for Excel Flattener.
"""

import argparse
import sys
from pathlib import Path

from flattener import flatten_workbook, setup_logging
from flattener.utils import print_summary, save_analysis_artifacts
from flattener.flattener import save_flattened_data


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description='Flatten Excel workbook into a flat file for LLM processing'
    )
    parser.add_argument(
        'input_file', 
        help='Path to the Excel workbook (.xlsx or .xlsm)'
    )
    parser.add_argument(
        '-o', '--output', 
        help='Output CSV file path (default: input_filename_flattened.csv)'
    )
    parser.add_argument(
        '--include-empty', 
        action='store_true',
        help='Include empty cells in output'
    )
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level'
    )
    parser.add_argument(
        '--log-file',
        help='Save logs to file'
    )
    parser.add_argument(
        '--save-artifacts',
        action='store_true',
        help='Save all analysis artifacts (CSV, metadata, preview) to analysis_output/ directory'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(level=args.log_level, log_file=args.log_file)
    
    try:
        print(f"Processing: {args.input_file}")
        
        # Flatten the workbook
        result = flatten_workbook(
            args.input_file, 
            include_empty_cells=args.include_empty
        )
        
        # Print summary
        print_summary(result)
        
        if args.save_artifacts:
            # Save all artifacts
            artifacts = save_analysis_artifacts(result)
            print(f"\nAnalysis artifacts saved:")
            for artifact_type, path in artifacts.items():
                print(f"- {artifact_type}: {path}")
        else:
            # Just save CSV
            output_path = save_flattened_data(result, args.output)
            print(f"\nFlattened data saved to: {output_path}")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()