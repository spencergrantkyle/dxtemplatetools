# Process Assessment Checklist 📋

## Is the current PDF enough to build a working LangGraph agent?

Use this checklist to evaluate if your process documentation is sufficient for building an automated LangGraph agent.

## Assessment Matrix

| Area                    | Coverage in your PDF | Gaps / Improvements | Status |
|------------------------|---------------------|---------------------|--------|
| **Trigger & scope**     | Document how the process starts (e.g., Slack message → UK triage flag → run `UKTemplateSupportAgent`) | Add *explicit* Slack channel IDs, regex/key-phrases, and a "not-UK" exit path so the agent won't run needlessly | ⬜ |
| **Tooling**             | List the custom tools needed (e.g., `search linksmaster`, `update linksmaster`, `technical_check`, `linksearchinmaster`, `GUID extractor`, `propose temporary fix`) | For each tool, document **signature** (inputs → outputs), expected error handling, and an example call | ⬜ |
| **Workflow logic**      | Describe decision points (e.g., "If applicable to UK THEN kickstart…") | Represent every branch in a truth-table so it can be copy-pasted into `graph.add_conditional_edges` | ⬜ |
| **Data & context**      | Document files/screenshots, Notion URLs, and local knowledge bases used | Add a table mapping *data source* ➜ *where it's stored* ➜ *access method* (path, API call, or LangGraph tool) | ⬜ |
| **Acceptance criteria** | Show the expected outcome (e.g., turned `N` → `Y` in LinkMaster and provided a manual workaround) | Include a "Definition of Done" checklist: ✔ template fields fixed ✔ unit test passes ✔ support ticket auto-reply sent | ⬜ |

## Detailed Assessment Questions

### 🎯 Trigger & Scope

- [ ] **Trigger Conditions**: Are the exact conditions for starting this process clearly defined?
- [ ] **Input Channels**: Are all input sources (Slack, email, tickets) explicitly listed?
- [ ] **Scope Boundaries**: Is it clear when this agent should NOT run?
- [ ] **Keywords/Patterns**: Are trigger keywords and patterns documented?
- [ ] **Exit Conditions**: Are early exit scenarios documented?

**Required for Agent**: Specific trigger patterns, channel IDs, and boolean logic for when to engage.

### 🛠️ Tooling

- [ ] **Tool Inventory**: Are all required tools listed?
- [ ] **Tool Signatures**: Is the input/output format documented for each tool?
- [ ] **Error Handling**: How should the agent handle tool failures?
- [ ] **Example Calls**: Are there working examples of each tool usage?
- [ ] **Dependencies**: Are tool dependencies and prerequisites clear?

**Required for Agent**: Complete tool signatures with examples and error handling strategies.

### 🔀 Workflow Logic

- [ ] **Decision Points**: Are all decision nodes clearly identified?
- [ ] **Branching Logic**: Is the condition for each branch explicit?
- [ ] **Truth Tables**: Can decision logic be expressed as boolean conditions?
- [ ] **Flow Visualization**: Is the complete flow documented (start to finish)?
- [ ] **Edge Cases**: Are unusual scenarios and their handling documented?

**Required for Agent**: Boolean conditions that can be directly coded into `graph.add_conditional_edges`.

### 📊 Data & Context

- [ ] **Data Sources**: Are all data sources identified and located?
- [ ] **Access Methods**: Is it clear how to access each data source?
- [ ] **Data Formats**: Are input/output formats specified?
- [ ] **Context Requirements**: What background information does the agent need?
- [ ] **State Management**: What information needs to be preserved between steps?

**Required for Agent**: Complete data source mapping with access patterns.

### ✅ Acceptance Criteria

- [ ] **Success Definition**: What constitutes a successful completion?
- [ ] **Quality Checks**: How can success be validated automatically?
- [ ] **Output Requirements**: What outputs are expected?
- [ ] **Notifications**: Who needs to be informed of completion?
- [ ] **Rollback Procedures**: How to undo if something goes wrong?

**Required for Agent**: Testable success criteria and validation procedures.

## Scoring

### ✅ Ready for Agent Development (80%+ coverage)
Your process documentation is comprehensive enough to build a working LangGraph agent. Proceed to the Notion template.

### ⚠️ Needs More Detail (50-79% coverage)
Significant gaps exist. Focus on the areas marked as incomplete before proceeding.

### ❌ Insufficient Documentation (<50% coverage)
The process needs substantial additional documentation before agent development can begin.

## Next Steps

### If Ready ✅
1. Move to the [Notion Template](../templates/notion_template.md)
2. Begin structured documentation
3. Plan your agent architecture

### If Not Ready ⚠️❌
1. Identify the biggest gaps from the assessment
2. Work with SMEs to gather missing information
3. Update process documentation
4. Re-run this assessment

## Assessment Notes

**Date**: ___________
**Assessor**: ___________
**Process Name**: ___________
**Overall Score**: _____ / 25 items (____%)

**Priority Gaps to Address**:
1. ________________________________
2. ________________________________
3. ________________________________

**Timeline for Completion**: ___________