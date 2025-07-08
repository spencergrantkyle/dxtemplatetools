# LangGraph Agent Examples 📚

This directory contains complete worked examples showing the entire process from documentation to deployed LangGraph agents.

## Available Examples

### 1. LLP (1A) LinkMap Update Agent

**Directory**: `llp_1a_linkmap_update/`

**Problem**: UK users reporting missing links in LLP (1A) templates because generation flags are set to 'N' instead of 'Y'.

**Solution**: Automated agent that detects UK-specific issues, searches for affected links, updates LinkMaster flags, and provides user feedback.

**Files**:
- [`notion_entry.md`](llp_1a_linkmap_update/notion_entry.md) - Complete Notion documentation
- [`generated_agent.py`](llp_1a_linkmap_update/generated_agent.py) - Generated LangGraph agent
- [`test_case.json`](llp_1a_linkmap_update/test_case.json) - Test input and expected output

**Learning Points**:
- How to structure triage logic for geographic routing
- Pattern for search → update → notify workflows
- Template generation with conditional logic
- Test case structure for validation

## Using These Examples

### 1. Study the Pattern
1. **Start with Notion documentation** - See how process knowledge is structured
2. **Examine the generated code** - Understand how documentation maps to implementation
3. **Review test cases** - Learn validation and quality assurance patterns

### 2. Adapt for Your Use Case
1. **Copy the Notion structure** for your own process documentation
2. **Modify the node types and logic** to match your workflow
3. **Update the tools and parameters** for your specific requirements
4. **Create comprehensive test cases** covering your edge cases

### 3. Generate and Test
1. **Use the CLI tool** to generate your agent from documentation
2. **Run the tests** to validate behavior
3. **Iterate on the documentation** to refine the agent logic

## Example Patterns

### Geographic/Scope Triage
**When to use**: Process applies only to specific regions, frameworks, or user types
**Pattern**: Early routing node that examines input for scope indicators
**Example**: UK vs non-UK routing in LLP example

### Search → Update → Notify
**When to use**: Process involves finding data, modifying it, and informing users
**Pattern**: Sequential nodes with validation between steps
**Example**: Find links → Update flags → Send reply

### Framework-Specific Logic
**When to use**: Different behaviors needed for different accounting frameworks
**Pattern**: Framework detection with conditional routing
**Example**: FRS102 vs FRS105 vs LLP SORP handling

### Error Handling and Rollback
**When to use**: Operations that can fail and need recovery
**Pattern**: Try-catch in nodes with error state tracking
**Example**: LinkMaster update failures with user notification

## Contributing New Examples

When adding new examples:

1. **Create the directory structure**:
   ```
   new_example/
   ├── notion_entry.md
   ├── generated_agent.py
   ├── test_case.json
   └── README.md (optional - for complex examples)
   ```

2. **Document the pattern** in this README
3. **Include comprehensive test cases** showing both success and failure scenarios
4. **Add explanatory comments** in the generated code highlighting key patterns

## Quick Reference

| Example | Pattern | Use Case | Complexity |
|---------|---------|----------|------------|
| LLP LinkMap Update | Geographic Triage + Search/Update | Regional support automation | ⭐⭐ |
| *Future examples...* | | | |

## Next Steps

- [ ] Add FRS102 template fix example
- [ ] Add multi-framework routing example
- [ ] Add error recovery and rollback example
- [ ] Add LLM-based content generation example