#!/usr/bin/env python3
"""
Demo script for GUID Formula Updater Tool

This script demonstrates how to use the GUID Formula Updater Tool
with sample data to classify accounting policy formulas.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.guid_formula_updater.main import process_guid_formulas
from tools.guid_formula_updater.utils import print_processing_summary
from shared.logger import setup_logging


async def run_demo():
    """Run the demo with sample data."""
    print("🚀 GUID Formula Updater Tool Demo")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ This demo requires an OpenAI API key.")
        print("Please set the OPENAI_API_KEY environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("\nTo run the demo without API calls, check the configuration and sample data files.")
        return
    
    # Setup paths
    workspace_root = Path(__file__).parent.parent.parent
    guid_file = workspace_root / "example_guid_list_for_formulas.csv"
    flattened_file = workspace_root / "example_flattened_data.csv"
    output_file = workspace_root / "demo_output_classified_formulas.csv"
    
    # Check if sample files exist
    if not guid_file.exists():
        print(f"❌ Sample GUID file not found: {guid_file}")
        return
    
    if not flattened_file.exists():
        print(f"❌ Sample flattened data file not found: {flattened_file}")
        return
    
    print(f"📁 Input files:")
    print(f"   GUID list: {guid_file}")
    print(f"   Flattened data: {flattened_file}")
    print(f"   Output: {output_file}")
    print()
    
    # Custom instruction for demo
    demo_instruction = """
    Review the accounting policy text and assign the UK FRS102 accounting standard and paragraph reference that is applicable.
    For demonstration purposes, provide detailed classifications where possible.
    If the text is not specifically attributable to a certain standard, mark it as "General FS Verbage".
    Return your response in this exact format: "FRS102 Section X.Y (Paragraph Z)" or "General FS Verbage".
    """
    
    try:
        print("🔄 Starting GUID formula processing...")
        print("   Note: This demo will make real OpenAI API calls (costs may apply)")
        print("   Processing sample accounting policy formulas...")
        print()
        
        # Setup logging for demo
        setup_logging(level="INFO")
        
        # Process the formulas
        result = await process_guid_formulas(
            guid_file_path=str(guid_file),
            flattened_file_path=str(flattened_file),
            output_path=str(output_file),
            instruction=demo_instruction
        )
        
        # Print results
        print_processing_summary(result)
        
        if result.output_path and Path(result.output_path).exists():
            print(f"\n📊 Results saved to: {result.output_path}")
            print("\n🔍 Sample classifications:")
            
            # Show first few classifications
            import pandas as pd
            df = pd.read_csv(result.output_path)
            
            if 'FRS102_Classification' in df.columns:
                for i, row in df.head(5).iterrows():
                    formula_text = str(row.get('Formula Text', ''))[:60]
                    classification = row.get('FRS102_Classification', 'N/A')
                    print(f"   • {formula_text}... → {classification}")
                
                if len(df) > 5:
                    print(f"   ... and {len(df) - 5} more classifications")
            
            print(f"\n✅ Demo completed successfully!")
            print(f"📄 Full results available in: {result.output_path}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your OpenAI API key is valid")
        print("2. Ensure you have internet connectivity")
        print("3. Try running with --verbose for more details")


def main():
    """Main entry point for demo."""
    print("GUID Formula Updater Tool - Demo Mode")
    print("This demo processes sample accounting policy data\n")
    
    # Run the async demo
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()