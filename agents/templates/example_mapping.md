# Notion to Code Mapping Guide 🔗

This document explains how each field in the Notion template maps to generated LangGraph agent code.

## Field Mappings

### Basic Information Fields

| Notion Field | Code Location | Usage | Example |
|--------------|---------------|--------|---------|
| **Title** | Class names, function names, module docstring | Creates the agent class name and unique identifiers | `LLP (1A) – LinkMap "N→Y"` → `LLPLinkMapAgent` |
| **Author / SME** | Module docstring header | Documentation and attribution | `# Author: John Smith` |
| **Problem Summary** | Module docstring | High-level description of what the agent solves | Added to class and module documentation |
| **Root Cause** | Module docstring | Technical context for the solution | Detailed explanation in docstring |

### Process Definition Fields

| Notion Field | Code Location | Usage | Example |
|--------------|---------------|--------|---------|
| **Temporary Fix Steps** | Module docstring, node comments | Documents the manual process being automated | Step-by-step comments in nodes |
| **Permanent Template Change** | Module docstring, update node logic | What the agent actually implements | Hard-coded in update operations |
| **Framework(s)** | Module docstring, tool parameters | Passed to framework-specific tools | `framework="FRS102(1A)"` |

### Agent Architecture Fields

| Notion Field | Code Location | Usage | Example |
|--------------|---------------|--------|---------|
| **LangGraph Nodes** | Node functions, graph construction | Creates `def node_name()` functions and `graph.add_node()` calls | Each row becomes a function |
| **Conditional Routes** | Edge functions, graph construction | Creates decision functions and `graph.add_conditional_edges()` calls | YAML → boolean logic |
| **Tools Needed** | Imports, tool wrapper functions | Generates imports and tool call wrappers | `from tools.search_linksmaster import search_linksmaster` |

### Data and State Fields

| Notion Field | Code Location | Usage | Example |
|--------------|---------------|--------|---------|
| **Affected Links / GUIDs** | State model, tool parameters | Hard-coded data passed to tools | `search_links = ["cl.524.000", "nl.524.000"]` |
| **Test Case(s)** | Test functions | Creates test input and expected output validation | `test_agent_with_case()` function |
| **Definition of Done** | Test validation, success criteria | Comments and validation logic | Success criteria checks |

## Detailed Mapping Examples

### 1. LangGraph Nodes Table → Node Functions

**Notion Input:**
| Node Name | Type | Inputs | Outputs | Description |
|-----------|------|--------|---------|-------------|
| triage_node | Router | messages | is_uk, framework | Determines if issue is UK-related |
| find_links_node | Tool | is_uk | link_hits | Searches for affected links |

**Generated Code:**
```python
def triage_node(state: AgentState) -> AgentState:
    """
    Determines if issue is UK-related
    
    Inputs: messages
    Outputs: is_uk, framework
    """
    # Implementation...
    return state

def find_links_node(state: AgentState) -> AgentState:
    """
    Searches for affected links
    
    Inputs: is_uk
    Outputs: link_hits
    """
    # Implementation...
    return state
```

### 2. Conditional Routes → Edge Logic

**Notion Input (YAML):**
```yaml
- source: triage_node
  when: state.is_uk
  dest: find_links_node
- source: triage_node
  when: not state.is_uk
  dest: reply_node
```

**Generated Code:**
```python
def decide_triage_node_next(state: AgentState) -> str:
    """Decision function for triage_node node."""
    if state.is_uk:
        return "find_links_node"
    if not state.is_uk:
        return "reply_node"
    return END

graph.add_conditional_edges(
    "triage_node",
    decide_triage_node_next,
    {
        "find_links_node": "find_links_node",
        "reply_node": "reply_node",
        END: END
    }
)
```

### 3. Affected Links/GUIDs → Tool Parameters

**Notion Input:**
| Link | Current Flag | New Flag | Framework |
|------|-------------|----------|-----------|
| cl.524.000 | N | Y | FRS102(1A) |
| nl.524.000 | N | Y | FRS102(1A) |

**Generated Code:**
```python
def update_linkmaster_node(state: AgentState) -> AgentState:
    try:
        for link_update in [
            {'link': 'cl.524.000', 'new_flag': 'Y'},
            {'link': 'nl.524.000', 'new_flag': 'Y'}
        ]:
            result = call_update_linksmaster(
                state,
                link=link_update['link'],
                framework="FRS102(1A)",
                new_flag=link_update['new_flag']
            )
    except Exception as e:
        # Error handling...
    return state
```

### 4. Tools Needed → Imports and Wrappers

**Notion Input:**
- search_linksmaster
- update_linksmaster
- send_slack_reply

**Generated Code:**
```python
# Imports
from tools.search_linksmaster import search_linksmaster
from tools.update_linksmaster import update_linksmaster
from tools.send_slack_reply import send_slack_reply

# Wrappers
def call_search_linksmaster(state: AgentState, **kwargs) -> Dict[str, Any]:
    try:
        result = search_linksmaster(**kwargs)
        state.actions_taken.append("search_linksmaster")
        return result
    except Exception as e:
        state.error_message = f"search_linksmaster failed: {str(e)}"
        return {}
```

### 5. Test Cases → Test Functions

**Notion Input (JSON):**
```json
{
  "input": {
    "slack_message": "UK user reporting missing cl.524.000 link",
    "framework": "FRS102"
  },
  "expected_output": {
    "success": true,
    "links_updated": ["cl.524.000", "nl.524.000"]
  }
}
```

**Generated Code:**
```python
def test_agent_with_case():
    test_case = {
        "input": {
            "slack_message": "UK user reporting missing cl.524.000 link",
            "framework": "FRS102"
        },
        "expected_output": {
            "success": True,
            "links_updated": ["cl.524.000", "nl.524.000"]
        }
    }
    
    initial_state = AgentState(
        messages=[{"content": test_case["input"]["slack_message"]}]
    )
    
    result = Agent.invoke(initial_state)
    # Validation logic...
```

## State Model Generation

The state model is automatically generated based on the fields referenced in your conditional routes and node definitions:

**Automatically Detected Fields:**
- `is_uk` → `is_uk: bool = False`
- `framework` → `framework: Optional[str] = None`
- `link_hits` → `link_hits: Dict[str, Any] = Field(default_factory=dict)`
- `proposed_updates` → `proposed_updates: List[str] = Field(default_factory=list)`

**Always Included Fields:**
- `messages: List[Dict[str, Any]]` - For conversation history
- `success: bool = False` - For tracking completion
- `error_message: Optional[str] = None` - For error handling
- `actions_taken: List[str]` - For audit trail

## Code Generation Process

1. **Parse Notion Data**: Extract all fields from the Notion page
2. **Analyze Dependencies**: Identify state fields needed based on routes and nodes
3. **Generate Templates**: Fill Jinja2 template with extracted data
4. **Validate Code**: Check for syntax and basic logic errors
5. **Apply Formatting**: Use black and isort for code formatting
6. **Generate Tests**: Create test functions from test cases

## Customization Points

### Adding Custom Node Logic

If you need custom implementation for a node, use the **Body** field in the LangGraph Nodes table:

**Notion Input:**
```python
# Custom validation logic
if not state.framework:
    state.error_message = "Framework not detected"
    return state

# Custom processing
state.custom_field = process_special_case(state.messages)
```

**Generated Code:**
The custom body is inserted directly into the node function.

### Adding Extra State Fields

Define additional state fields that aren't automatically detected by adding them to a custom template section or by extending the generated state model after generation.

## Troubleshooting

### Common Issues

1. **Missing State Fields**: If routes reference fields that aren't in the state model, add them to the extra_state_fields section
2. **Tool Import Errors**: Ensure all tools in "Tools Needed" exist in the tools/ directory
3. **Invalid Route Logic**: Conditional routes must be valid Python boolean expressions
4. **Node Type Mismatches**: Ensure node types match their intended implementation (LLM, Tool, Router, etc.)

### Validation Checklist

Before generating:
- [ ] All conditional routes reference valid state fields
- [ ] All tools in "Tools Needed" are available
- [ ] Node names are valid Python identifiers (snake_case)
- [ ] Test cases have both input and expected_output
- [ ] No circular dependencies in node routes