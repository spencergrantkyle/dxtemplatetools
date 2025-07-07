#!/usr/bin/env python3
"""
DXTEMPLATETOOLS Launcher - Central entry point for all tools.

This launcher dynamically imports and runs tools from the tools/ directory.
Each tool must have a main.py file with a main() function.
"""

import argparse
import sys
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from shared.logger import setup_logging, get_logger

logger = get_logger(__name__)


def discover_tools() -> Dict[str, Path]:
    """
    Discover available tools in the tools/ directory.
    
    Returns:
        Dict[str, Path]: Mapping of tool names to their directory paths
    """
    tools_dir = Path(__file__).parent / "tools"
    available_tools = {}
    
    if not tools_dir.exists():
        return available_tools
    
    for tool_path in tools_dir.iterdir():
        if tool_path.is_dir() and (tool_path / "main.py").exists():
            tool_name = tool_path.name
            available_tools[tool_name] = tool_path
    
    return available_tools


def load_tool_config(tool_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load tool configuration from config.yaml if it exists.
    
    Args:
        tool_path: Path to the tool directory
        
    Returns:
        Optional[Dict]: Configuration dictionary or None
    """
    config_file = tool_path / "config.yaml"
    if not config_file.exists():
        return None
    
    try:
        import yaml
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        logger.warning("PyYAML not installed, skipping config loading")
        return None
    except Exception as e:
        logger.warning(f"Failed to load config for {tool_path.name}: {e}")
        return None


def run_tool(tool_name: str, tool_args: list) -> int:
    """
    Run a specific tool with the given arguments.
    
    Args:
        tool_name: Name of the tool to run
        tool_args: Arguments to pass to the tool
        
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    available_tools = discover_tools()
    
    if tool_name not in available_tools:
        print(f"❌ Error: Tool '{tool_name}' not found.")
        print(f"Available tools: {', '.join(available_tools.keys())}")
        return 1
    
    tool_path = available_tools[tool_name]
    main_file = tool_path / "main.py"
    
    try:
        # Load tool configuration
        config = load_tool_config(tool_path)
        if config:
            logger.info(f"Loaded config for {tool_name}: {config.get('description', 'No description')}")
        
        # Dynamically import the tool's main module
        spec = importlib.util.spec_from_file_location(f"{tool_name}.main", main_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module spec for {main_file}")
        
        module = importlib.util.module_from_spec(spec)
        
        # Replace sys.argv with tool-specific arguments
        original_argv = sys.argv.copy()
        sys.argv = [str(main_file)] + tool_args
        
        try:
            # Load and execute the module
            spec.loader.exec_module(module)
            
            # Call the main function
            if hasattr(module, 'main'):
                logger.info(f"Running {tool_name} with args: {tool_args}")
                module.main()
                return 0
            else:
                logger.error(f"Tool {tool_name} does not have a main() function")
                return 1
                
        finally:
            # Restore original sys.argv
            sys.argv = original_argv
            
    except Exception as e:
        logger.error(f"Failed to run tool {tool_name}: {e}")
        print(f"❌ Error running {tool_name}: {e}")
        return 1


def list_tools():
    """List all available tools with their descriptions."""
    available_tools = discover_tools()
    
    if not available_tools:
        print("No tools found in the tools/ directory.")
        return
    
    print("🛠️  Available DXTEMPLATETOOLS:")
    print("=" * 50)
    
    for tool_name, tool_path in available_tools.items():
        # Try to load description from config
        config = load_tool_config(tool_path)
        description = "No description available"
        
        if config and 'description' in config:
            description = config['description']
        else:
            # Try to get description from main.py docstring
            main_file = tool_path / "main.py"
            try:
                with open(main_file, 'r') as f:
                    content = f.read()
                    if '"""' in content:
                        docstring = content.split('"""')[1].strip()
                        description = docstring.split('\n')[0]
            except Exception:
                pass
        
        print(f"📁 {tool_name}")
        print(f"   {description}")
        print()


def main():
    """Main launcher entry point."""
    parser = argparse.ArgumentParser(
        description='DXTEMPLATETOOLS Launcher - Run tools from the tools/ directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py --list                           # List available tools
  python launcher.py --tool excel_flattener input.xlsx # Run excel_flattener
  python launcher.py --tool guid_extractor frs.xlsx guids.csv  # Run guid_extractor
  python launcher.py --tool excel_flattener --help    # Get tool-specific help
        """
    )
    
    parser.add_argument('--tool', '-t', help='Name of the tool to run')
    parser.add_argument('--list', '-l', action='store_true', help='List available tools')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--log-file', help='Log to file instead of console')
    
    # Parse known args to separate launcher args from tool args
    launcher_args, tool_args = parser.parse_known_args()
    
    # Setup logging
    log_level = "DEBUG" if launcher_args.verbose else "INFO"
    setup_logging(level=log_level, log_file=launcher_args.log_file)
    
    # Handle list command
    if launcher_args.list:
        list_tools()
        return 0
    
    # Handle tool execution
    if launcher_args.tool:
        return run_tool(launcher_args.tool, tool_args)
    
    # No action specified
    parser.print_help()
    print("\n💡 Use --list to see available tools or --tool <name> to run a specific tool")
    return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)