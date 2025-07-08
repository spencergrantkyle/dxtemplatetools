# LLP (1A) – LinkMap "N→Y" – 2025-07-08

> **Example Notion Entry**: This represents how the process would be documented in your Notion database using the template structure.

## Basic Information

| Field | Value |
|-------|-------|
| **Title** | LLP (1A) – LinkMap "N→Y" – 2025-07-08 |
| **Author / SME** | Sarah Mitchell |
| **Slack Thread URL** | https://draftworx.slack.com/archives/C1234567890/p1234567890123456 |
| **Framework(s)** | LLP SORP (1A) |
| **Agent Status** | Ready for Generation |

## Problem Definition

### Problem Summary
Link `cl.524.000` not showing because FRS102 (1A) flag = `N`.

### Root Cause
LinkMaster generation flag incorrect for FRS102 (1A) framework.

### Temporary Fix Steps
1. In WTB click blue box → Import links…
2. Select the missing links manually  
3. Confirm import and verify display

### Permanent Template Change
1. Change `cl.524.000` generation flag from `N` to `Y` for FRS102 (1A)
2. Change `nl.524.000` generation flag from `N` to `Y` for FRS102 (1A)
3. Update template validation rules

## Agent Architecture

### Tools Needed
- `search_linksmaster`
- `update_linksmaster`
- `send_slack_reply`

### LangGraph Nodes

| Node Name | Type | Inputs | Outputs | Description |
|-----------|------|--------|---------|-------------|
| `triage_node` | Router | `messages` | `is_uk`, `framework` | Determines if issue is UK-related and extracts framework |
| `find_links_node` | Tool | `is_uk` | `link_hits` | Searches LinkMaster for affected links |
| `update_linkmaster_node` | Tool | `link_hits` | `proposed_updates` | Updates generation flags from N to Y |
| `reply_node` | Tool | `proposed_updates`, `success` | `messages` | Sends formatted reply to Slack |

### Conditional Routes (YAML)
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
  dest: reply_node
- source: update_linkmaster_node
  when: state.success
  dest: reply_node
```

## Data and Testing

### Affected Links / GUIDs

| Link | Current Flag | New Flag | Framework | GUID |
|------|-------------|----------|-----------|------|
| cl.524.000 | N | Y | FRS102(1A) | 12345678 |
| nl.524.000 | N | Y | FRS102(1A) | 87654321 |

### Test Case(s)
```json
{
  "input": {
    "slack_message": "UK user reporting missing cl.524.000 link in FRS102 (1A)",
    "framework": "FRS102",
    "variant": "1A",
    "user_location": "UK"
  },
  "expected_output": {
    "actions_taken": ["search_linksmaster", "update_linksmaster", "send_slack_reply"],
    "links_updated": ["cl.524.000", "nl.524.000"],
    "flags_changed": [
      {"link": "cl.524.000", "from": "N", "to": "Y"},
      {"link": "nl.524.000", "from": "N", "to": "Y"}
    ],
    "reply_sent": true,
    "success": true
  }
}
```

### Definition of Done
- [x] Template flags changed from N to Y
- [x] Unit test passes with new configuration  
- [x] Support ticket auto-reply sent
- [x] LinkMaster updated successfully
- [x] Changes validated in test environment

## External References
- FRS102 (1A) Framework Documentation: [Link to PDF]
- LinkMaster Generation Rules: [Internal Wiki]
- Support Thread Screenshots: [Attached files]

## Implementation Notes

### Edge Cases Handled
1. **Non-UK Users**: Early exit with standard reply directing to general support
2. **Missing Links**: If search returns no results, notify user and escalate
3. **Update Failures**: Rollback any partial changes and notify support team
4. **Framework Detection**: If framework can't be determined, default to manual escalation

### Success Metrics
- Reduction in manual LinkMaster updates for UK FRS102 (1A) issues
- Faster response time for UK users reporting missing links
- Consistent application of template fixes

### Future Enhancements
- Extend to other frameworks (FRS105, Charity SORP)
- Add automatic validation after updates
- Include user notification of fix completion