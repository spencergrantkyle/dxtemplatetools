#!/usr/bin/env python3
"""
Example script demonstrating how to integrate Excel Flattener with AI agents.
This shows the integration pattern for Draftworx AI Agent workflows.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from flattener import flatten_workbook, setup_logging, log_run_to_file
from flattener.utils import create_analysis_preview, save_analysis_artifacts


# Mock AI agent functions (replace with actual LangChain/LangGraph implementation)
def analyze_flattened_excel(flattened_preview: str) -> List[Dict[str, Any]]:
    """
    Mock function representing LLM analysis of flattened Excel data.
    
    In practice, this would be your LangChain agent that:
    1. Takes the flattened data preview
    2. Analyzes structure, finds issues, suggests improvements
    3. Returns structured instructions
    
    Args:
        flattened_preview (str): Preview text of flattened Excel data
        
    Returns:
        List[Dict]: Structured instructions for data cleanup/modification
    """
    # This is a mock response - replace with actual LLM call
    mock_instructions = [
        {
            "action": "flag_inconsistency",
            "sheet": "Income Statement",
            "issue": "Potential typo in header",
            "description": "Found 'Revnue' which might be 'Revenue'",
            "suggested_fix": "rename_header",
            "confidence": 0.9
        },
        {
            "action": "suggest_cleanup",
            "sheet": "Balance Sheet", 
            "issue": "Empty rows detected",
            "description": "Rows 15-20 appear to be formatting rows with no data",
            "suggested_fix": "remove_empty_rows",
            "confidence": 0.8
        },
        {
            "action": "validate_formulas",
            "sheet": "Calculations",
            "issue": "Complex formula detected",
            "description": "Formula in C25 references multiple sheets - verify accuracy",
            "suggested_fix": "manual_review",
            "confidence": 0.7
        }
    ]
    
    print("🤖 AI Agent Analysis Complete")
    return mock_instructions


def generate_improvement_suggestions(instructions: List[Dict[str, Any]]) -> str:
    """
    Generate human-readable improvement suggestions from AI instructions.
    
    Args:
        instructions (List[Dict]): AI-generated instructions
        
    Returns:
        str: Formatted suggestions
    """
    suggestions = []
    
    for i, instruction in enumerate(instructions, 1):
        confidence_emoji = "🟢" if instruction["confidence"] > 0.8 else "🟡" if instruction["confidence"] > 0.6 else "🔴"
        
        suggestion = f"""
{i}. {instruction['action'].replace('_', ' ').title()}
   Sheet: {instruction['sheet']}
   Issue: {instruction['issue']}
   Description: {instruction['description']}
   Suggested Fix: {instruction['suggested_fix'].replace('_', ' ').title()}
   Confidence: {confidence_emoji} {instruction['confidence']:.1%}
"""
        suggestions.append(suggestion)
    
    return "\n".join(suggestions)


@log_run_to_file("ExcelFlattenerAIWorkflow")
def process_excel_with_ai(file_path: str, save_artifacts: bool = True) -> Dict[str, Any]:
    """
    Complete workflow: Flatten Excel → AI Analysis → Generate Instructions
    
    This demonstrates the integration pattern for your Draftworx AI Agent.
    
    Args:
        file_path (str): Path to Excel file
        save_artifacts (bool): Whether to save all analysis artifacts
        
    Returns:
        Dict: Complete workflow results
    """
    print(f"🔄 Starting AI-powered Excel analysis for: {file_path}")
    
    # Step 1: Flatten the Excel workbook
    print("📊 Step 1: Flattening Excel workbook...")
    result = flatten_workbook(file_path)
    
    # Step 2: Create preview for AI analysis
    print("📝 Step 2: Creating analysis preview...")
    preview = create_analysis_preview(result, max_rows=20)
    
    # Step 3: AI Analysis (this would be your LangChain agent)
    print("🤖 Step 3: Running AI analysis...")
    instructions = analyze_flattened_excel(preview)
    
    # Step 4: Generate human-readable suggestions
    print("💡 Step 4: Generating improvement suggestions...")
    suggestions = generate_improvement_suggestions(instructions)
    
    # Step 5: Save artifacts if requested
    if save_artifacts:
        print("💾 Step 5: Saving analysis artifacts...")
        artifacts = save_analysis_artifacts(result)
        
        # Save AI instructions
        input_name = Path(file_path).stem
        instructions_path = Path("analysis_output") / f"{input_name}_ai_instructions.json"
        with open(instructions_path, 'w') as f:
            json.dump(instructions, f, indent=2)
        
        # Save human-readable suggestions
        suggestions_path = Path("analysis_output") / f"{input_name}_suggestions.txt"
        with open(suggestions_path, 'w') as f:
            f.write(f"AI-Generated Improvement Suggestions\n{'='*40}\n")
            f.write(f"File: {file_path}\n")
            f.write(f"Analysis Date: {result.total_cells} cells processed\n\n")
            f.write(suggestions)
        
        artifacts["ai_instructions"] = str(instructions_path)
        artifacts["suggestions"] = str(suggestions_path)
    else:
        artifacts = {}
    
    workflow_result = {
        "flatten_result": result,
        "ai_instructions": instructions,
        "suggestions": suggestions,
        "artifacts": artifacts
    }
    
    print("✅ AI workflow complete!")
    return workflow_result


def main():
    """Example usage of the AI workflow."""
    # Set up logging
    setup_logging(level="INFO")
    
    # Example Excel file path (you would replace this with actual file)
    example_file = "example_workbook.xlsx"
    
    # Check if example file exists
    if not Path(example_file).exists():
        print(f"⚠️  Example file '{example_file}' not found.")
        print("To test this workflow:")
        print("1. Place an Excel file in the current directory")
        print("2. Update the 'example_file' variable with the correct path")
        print("3. Run this script again")
        return
    
    try:
        # Run the complete AI workflow
        results = process_excel_with_ai(example_file)
        
        # Display results
        print("\n" + "="*50)
        print("WORKFLOW RESULTS")
        print("="*50)
        
        print(f"\n📊 Flattening Results:")
        print(f"   • Total cells: {results['flatten_result'].total_cells:,}")
        print(f"   • Sheets: {results['flatten_result'].sheets_processed}")
        print(f"   • Value types: {len(results['flatten_result'].value_types)}")
        
        print(f"\n🤖 AI Analysis:")
        print(f"   • Instructions generated: {len(results['ai_instructions'])}")
        
        print(f"\n💡 Suggestions:")
        print(results['suggestions'])
        
        if results['artifacts']:
            print(f"\n💾 Saved Artifacts:")
            for name, path in results['artifacts'].items():
                print(f"   • {name}: {path}")
                
    except Exception as e:
        print(f"❌ Error in AI workflow: {e}")


if __name__ == "__main__":
    main()