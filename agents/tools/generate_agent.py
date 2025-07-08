#!/usr/bin/env python3
"""
CLI tool for generating LangGraph agents from Notion templates.

Usage:
    python generate_agent.py --notion-page-id <page_id>
    python generate_agent.py --json-file <file_path>
    python generate_agent.py --validate-template <template_path>

Example:
    python generate_agent.py --notion-page-id abc123def456 --output agents/generated/
    python generate_agent.py --json-file exported_process.json --test-mode
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from jinja2 import Environment, FileSystemLoader, Template
    import yaml
    from pydantic import BaseModel, ValidationError
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Install with: pip install jinja2 pyyaml pydantic")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Template directory path
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
EXAMPLES_DIR = Path(__file__).parent.parent / "examples" 
OUTPUT_DIR = Path(__file__).parent.parent / "generated"

class NotionTemplateData(BaseModel):
    """Pydantic model for validating Notion template data."""
    title: str
    author: str
    slack_thread_url: Optional[str] = None
    frameworks: List[str]
    problem_summary: str
    root_cause: str
    temporary_fix_steps: List[str]
    permanent_template_changes: List[str]
    affected_links_guids: List[Dict[str, str]]
    tools_needed: List[str]
    external_references: Optional[List[str]] = None
    langgraph_nodes: List[Dict[str, str]]
    conditional_routes: List[Dict[str, str]]
    definition_of_done: List[str]
    test_cases: List[Dict[str, Any]]
    agent_status: Optional[str] = "Generated"

def load_notion_data_from_json(file_path: str) -> Dict[str, Any]:
    """Load Notion template data from JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded data from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {e}")
        raise

def load_notion_data_from_api(page_id: str) -> Dict[str, Any]:
    """Load Notion template data from Notion API."""
    # TODO: Implement actual Notion API integration
    logger.warning("Notion API integration not yet implemented")
    
    # For now, return mock data structure
    mock_data = {
        "title": "Example Agent",
        "author": "Mock Author",
        "frameworks": ["FRS102"],
        "problem_summary": "Example problem",
        "root_cause": "Example root cause", 
        "temporary_fix_steps": ["Step 1", "Step 2"],
        "permanent_template_changes": ["Change 1", "Change 2"],
        "affected_links_guids": [
            {"link": "cl.524.000", "current_flag": "N", "new_flag": "Y", "framework": "FRS102"}
        ],
        "tools_needed": ["search_linksmaster", "update_linksmaster"],
        "langgraph_nodes": [
            {"name": "triage_node", "type": "Router", "inputs": "messages", "outputs": "is_uk", "description": "Triage logic"}
        ],
        "conditional_routes": [
            {"source": "triage_node", "when": "state.is_uk", "dest": "action_node"}
        ],
        "definition_of_done": ["Test passes", "Reply sent"],
        "test_cases": [
            {
                "input": {"slack_message": "Test message"},
                "expected_output": {"success": True}
            }
        ]
    }
    
    logger.info(f"Mock data loaded for page ID: {page_id}")
    return mock_data

def validate_template_data(data: Dict[str, Any]) -> NotionTemplateData:
    """Validate template data against schema."""
    try:
        validated_data = NotionTemplateData(**data)
        logger.info("Template data validation successful")
        return validated_data
    except ValidationError as e:
        logger.error(f"Template data validation failed: {e}")
        raise

def parse_conditional_routes(routes_yaml: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Parse and validate conditional routes."""
    parsed_routes = []
    
    for route in routes_yaml:
        if isinstance(route, dict) and all(key in route for key in ['source', 'when', 'dest']):
            parsed_routes.append(route)
        else:
            logger.warning(f"Invalid route format: {route}")
    
    return parsed_routes

def generate_agent_code(template_data: NotionTemplateData) -> str:
    """Generate LangGraph agent code from template data."""
    try:
        # Set up Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Load the template
        template = env.get_template("langgraph_agent_template.py.j2")
        
        # Prepare template variables
        template_vars = {
            "title": template_data.title,
            "author": template_data.author,
            "frameworks": template_data.frameworks,
            "problem_summary": template_data.problem_summary,
            "root_cause": template_data.root_cause,
            "temporary_fix_steps": template_data.temporary_fix_steps,
            "permanent_template_changes": template_data.permanent_template_changes,
            "affected_links_guids": template_data.affected_links_guids,
            "tools_needed": template_data.tools_needed,
            "langgraph_nodes": template_data.langgraph_nodes,
            "conditional_routes": parse_conditional_routes(template_data.conditional_routes),
            "definition_of_done": template_data.definition_of_done,
            "test_cases": template_data.test_cases,
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "extra_state_fields": []  # TODO: Extract from routes analysis
        }
        
        # Render the template
        generated_code = template.render(**template_vars)
        logger.info("Agent code generation successful")
        return generated_code
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise

def save_generated_agent(code: str, template_data: NotionTemplateData, output_dir: str) -> str:
    """Save generated agent code to file."""
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename from title
        filename = template_data.title.lower()
        filename = "".join(c if c.isalnum() or c in "- " else "" for c in filename)
        filename = filename.replace(" ", "_").replace("-", "_") + "_agent.py"
        
        file_path = output_path / filename
        
        # Write the code to file
        with open(file_path, 'w') as f:
            f.write(code)
        
        logger.info(f"Generated agent saved to: {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Failed to save generated agent: {e}")
        raise

def run_basic_validation(file_path: str) -> bool:
    """Run basic validation on generated agent code."""
    try:
        # Check if file is valid Python syntax
        with open(file_path, 'r') as f:
            code = f.read()
        
        compile(code, file_path, 'exec')
        logger.info("Generated code syntax validation passed")
        
        # TODO: Add more sophisticated validation
        # - Check for required imports
        # - Validate LangGraph structure
        # - Run basic tests
        
        return True
        
    except SyntaxError as e:
        logger.error(f"Syntax error in generated code: {e}")
        return False
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False

def create_test_file(template_data: NotionTemplateData, output_dir: str) -> str:
    """Create a test file for the generated agent."""
    try:
        test_content = f"""#!/usr/bin/env python3
\"\"\"
Test file for {template_data.title} agent.
Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
\"\"\"

import unittest
import json
from pathlib import Path

# Import the generated agent (adjust path as needed)
# from {template_data.title.lower().replace(' ', '_')}_agent import *

class Test{template_data.title.replace(' ', '').replace('–', '').replace('-', '')}Agent(unittest.TestCase):
    \"\"\"Test cases for {template_data.title} agent.\"\"\"
    
    def setUp(self):
        \"\"\"Set up test fixtures.\"\"\"
        self.test_cases = {json.dumps(template_data.test_cases, indent=8)}
    
    def test_basic_functionality(self):
        \"\"\"Test basic agent functionality.\"\"\"
        # TODO: Implement actual test logic
        self.assertTrue(True, "Placeholder test")
    
    def test_edge_cases(self):
        \"\"\"Test edge cases.\"\"\"
        # TODO: Implement edge case tests
        pass
    
    def test_validation_criteria(self):
        \"\"\"Test against definition of done criteria.\"\"\"
        criteria = {template_data.definition_of_done}
        # TODO: Implement validation tests
        pass

if __name__ == '__main__':
    unittest.main()
"""
        
        # Save test file
        output_path = Path(output_dir)
        filename = f"test_{template_data.title.lower().replace(' ', '_').replace('-', '_')}_agent.py"
        test_file_path = output_path / filename
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        logger.info(f"Test file created: {test_file_path}")
        return str(test_file_path)
        
    except Exception as e:
        logger.error(f"Failed to create test file: {e}")
        raise

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Generate LangGraph agents from Notion templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --notion-page-id abc123def456
  %(prog)s --json-file process.json --output ./generated/
  %(prog)s --validate-template ./templates/example.json
        """
    )
    
    # Input source (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--notion-page-id",
        help="Notion page ID to fetch template data from"
    )
    input_group.add_argument(
        "--json-file",
        help="JSON file containing template data"
    )
    input_group.add_argument(
        "--validate-template",
        help="Validate template format without generating"
    )
    
    # Output options
    parser.add_argument(
        "--output",
        default=str(OUTPUT_DIR),
        help=f"Output directory for generated files (default: {OUTPUT_DIR})"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Generate and run basic tests"
    )
    parser.add_argument(
        "--no-validation",
        action="store_true",
        help="Skip code validation step"
    )
    
    # Logging options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load template data
        if args.notion_page_id:
            logger.info(f"Loading data from Notion page: {args.notion_page_id}")
            template_data_dict = load_notion_data_from_api(args.notion_page_id)
        elif args.json_file:
            logger.info(f"Loading data from JSON file: {args.json_file}")
            template_data_dict = load_notion_data_from_json(args.json_file)
        elif args.validate_template:
            logger.info(f"Validating template: {args.validate_template}")
            template_data_dict = load_notion_data_from_json(args.validate_template)
            validated_data = validate_template_data(template_data_dict)
            print("✅ Template validation successful!")
            return
        
        # Validate template data
        template_data = validate_template_data(template_data_dict)
        
        # Generate agent code
        logger.info("Generating agent code...")
        generated_code = generate_agent_code(template_data)
        
        # Save generated agent
        agent_file_path = save_generated_agent(generated_code, template_data, args.output)
        
        # Run validation unless disabled
        if not args.no_validation:
            logger.info("Running code validation...")
            validation_passed = run_basic_validation(agent_file_path)
            if not validation_passed:
                logger.warning("Code validation failed - manual review required")
        
        # Generate test file if requested
        if args.test_mode:
            logger.info("Generating test file...")
            test_file_path = create_test_file(template_data, args.output)
            print(f"Test file created: {test_file_path}")
        
        print(f"✅ Agent generation completed successfully!")
        print(f"Generated agent: {agent_file_path}")
        print(f"Title: {template_data.title}")
        print(f"Framework(s): {', '.join(template_data.frameworks)}")
        print(f"Tools needed: {', '.join(template_data.tools_needed)}")
        print(f"Nodes: {len(template_data.langgraph_nodes)}")
        print(f"Routes: {len(template_data.conditional_routes)}")
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()