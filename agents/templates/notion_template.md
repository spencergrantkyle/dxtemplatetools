# Notion Process-to-Agent Master Template 📝

> **Tip:** Store this as a Notion *database* template so every new row automatically populates the same fields.

## Database Schema

| Field                         | Type                    | Purpose                                    | Required |
|-------------------------------|-------------------------|--------------------------------------------|----------|
| **Title**                     | Text                    | `<Framework> – <Issue> – <Date>`          | ✅       |
| **Author / SME**              | Person                  | Who documented it                          | ✅       |
| **Slack Thread URL**          | URL                     | Original support context                   | ✅       |
| **Framework(s)**              | Multi-select            | FRS102, FRS105, LLP SORP…                  | ✅       |
| **Problem Summary**           | Text                    | One-liner in user language                | ✅       |
| **Root Cause**                | Text                    | Internal diagnosis                         | ✅       |
| **Temporary Fix Steps**       | Numbered list           | Copy-ready reply for support               | ✅       |
| **Permanent Template Change** | Numbered list           | What needs altering                        | ✅       |
| **Affected Links / GUIDs**    | Relation (Table)        | Links to GUID table with details          | ✅       |
| **Tools Needed**              | Multi-select            | search linksmaster, GUID extractor…       | ✅       |
| **External References**       | Files / URLs            | PDFs, standards, screenshots               | ⬜       |
| **LangGraph Nodes**           | Relation (Sub-table)    | Links to Nodes table                       | ✅       |
| **Conditional Routes**        | Code block (YAML)       | Decision logic                             | ✅       |
| **Definition of Done**        | Checkbox list           | Validation items                           | ✅       |
| **Test Case(s)**              | Code / JSON             | Example input → expected output            | ✅       |
| **Agent Status**              | Select                  | Draft, Ready, Generated, Deployed, Failed | ✅       |
| **Last Generated**            | Date                    | When agent was last generated              | ⬜       |
| **Generated Agent Path**      | Text                    | Path to generated agent file               | ⬜       |

## Sub-Tables

### LangGraph Nodes Table

| Field           | Type         | Purpose                              | Required |
|-----------------|--------------|--------------------------------------|----------|
| **Node Name**   | Text         | snake_case function name             | ✅       |
| **Type**        | Select       | LLM / Tool / Router / Condition      | ✅       |
| **Inputs**      | Text         | Expected inputs from state           | ✅       |
| **Outputs**     | Text         | What gets added to state             | ✅       |
| **Description** | Text         | What this node does                  | ✅       |
| **Body**        | Code block   | Function implementation (optional)   | ⬜       |

### Affected Links / GUIDs Table

| Field         | Type   | Purpose                           | Required |
|---------------|--------|-----------------------------------|----------|
| **Link**      | Text   | Link identifier (e.g., cl.524.000) | ✅       |
| **Current Flag** | Text | Current value                     | ✅       |
| **New Flag**  | Text   | Target value                      | ✅       |
| **GUID**      | Text   | Associated GUID                   | ⬜       |
| **Framework** | Text   | Which framework this applies to   | ✅       |

## Field Details & Examples

### Title
**Format**: `<Framework> – <Issue> – <Date>`
**Example**: `LLP (1A) – LinkMap "N→Y" – 2025-07-08`

### Problem Summary
**Format**: One clear sentence describing the user-facing issue
**Example**: `Link cl.524.000 not showing because FRS102 (1A) flag = N.`

### Root Cause
**Format**: Technical explanation of why this happens
**Example**: `LinkMaster generation flag incorrect for FRS102 (1A) framework.`

### Temporary Fix Steps
**Format**: Numbered list of manual steps
**Example**:
```
1. In WTB click blue box → Import links…
2. Select the missing links manually
3. Confirm import and verify display
```

### Permanent Template Change
**Format**: Numbered list of template modifications needed
**Example**:
```
1. Change cl.524.000 generation flag from N to Y for FRS102 (1A)
2. Change nl.524.000 generation flag from N to Y for FRS102 (1A)
3. Update template validation rules
```

### Tools Needed
**Options**: 
- `search_linksmaster`
- `update_linksmaster`
- `technical_check`
- `linksearchinmaster`
- `guid_extractor`
- `propose_temporary_fix`
- `send_slack_reply`
- `validate_template`

### Conditional Routes
**Format**: YAML structure defining decision logic
**Example**:
```yaml
- source: triage_node
  when: state.is_uk
  dest: find_links_node
- source: triage_node
  when: not state.is_uk
  dest: reply_node
- source: find_links_node
  when: state.link_hits
  dest: update_linkmaster_node
- source: find_links_node
  when: not state.link_hits
  dest: no_action_node
```

### Definition of Done
**Format**: Checkbox list of completion criteria
**Example**:
```
☐ Template flags changed from N to Y
☐ Unit test passes with new configuration
☐ Support ticket auto-reply sent
☐ LinkMaster updated successfully
☐ Changes validated in test environment
```

### Test Case(s)
**Format**: JSON with input and expected output
**Example**:
```json
{
  "input": {
    "slack_message": "UK user reporting missing cl.524.000 link in FRS102 (1A)",
    "framework": "FRS102",
    "variant": "1A",
    "user_location": "UK"
  },
  "expected_output": {
    "actions_taken": ["update_linkmaster"],
    "links_updated": ["cl.524.000", "nl.524.000"],
    "flags_changed": [{"link": "cl.524.000", "from": "N", "to": "Y"}],
    "reply_sent": true,
    "success": true
  }
}
```

## Template Creation Steps

### 1. Create the Main Database
1. In Notion, create a new database
2. Add all fields from the schema above
3. Configure field types and options
4. Set up the template with default values

### 2. Create Sub-Tables
1. Create "LangGraph Nodes" database
2. Create "Affected Links/GUIDs" database
3. Set up relations between main table and sub-tables

### 3. Configure Multi-Select Options

**Framework(s) Options**:
- FRS102
- FRS105
- LLP SORP
- Charity SORP
- Academy Accounts
- Micro-entities

**Tools Needed Options**:
- search_linksmaster
- update_linksmaster
- technical_check
- linksearchinmaster
- guid_extractor
- propose_temporary_fix
- send_slack_reply
- validate_template

**Agent Status Options**:
- Draft
- Ready for Generation
- Generated
- Deployed
- Failed
- Deprecated

**Node Type Options**:
- LLM
- Tool
- Router
- Condition
- Action

### 4. Set Up Templates
1. Create a template entry with all fields pre-populated
2. Add placeholder text for guidance
3. Set default values where appropriate

## Usage Workflow

1. **Create New Entry**: Use the template to create a new process documentation
2. **Fill Required Fields**: Complete all required fields with SME input
3. **Define Nodes**: Break down the process into discrete LangGraph nodes
4. **Map Routes**: Define the decision logic between nodes
5. **Add Test Cases**: Create comprehensive test scenarios
6. **Mark Ready**: Change status to "Ready for Generation"
7. **Generate Agent**: Use the CLI tool to generate the LangGraph agent

## Quality Checklist

Before marking as "Ready for Generation":

- [ ] All required fields completed
- [ ] At least 3 LangGraph nodes defined
- [ ] Conditional routes cover all decision points
- [ ] Test cases include edge cases
- [ ] Definition of Done is specific and testable
- [ ] SME has reviewed and approved

## Integration with Generation Pipeline

This Notion template is designed to be consumed by the agent generation CLI tool:

```bash
# Generate agent from Notion page
dwx generate-agent --notion-page-id <page_id>

# Generate agent from exported JSON
dwx generate-agent --json-file exported_process.json
```

The CLI tool will:
1. Fetch the Notion page data
2. Validate completeness
3. Generate the LangGraph agent code
4. Run initial tests
5. Update the Notion page with generation status