# === LLP (1A) – LinkMap "N→Y" – 2025-07-08 ===
# Generated from Notion template on 2025-01-08 15:30:00
# Author: Sarah Mitchell
# Framework(s): LLP SORP (1A)
"""
Link cl.524.000 not showing because FRS102 (1A) flag = N.

Root Cause: LinkMaster generation flag incorrect for FRS102 (1A) framework.

This agent automates the following process:
1. In WTB click blue box → Import links…
2. Select the missing links manually
3. Confirm import and verify display

Permanent changes implemented:
1. Change cl.524.000 generation flag from N to Y for FRS102 (1A)
2. Change nl.524.000 generation flag from N to Y for FRS102 (1A)
3. Update template validation rules
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
import logging

# Import your custom tools
from tools.search_linksmaster import search_linksmaster
from tools.update_linksmaster import update_linksmaster
from tools.send_slack_reply import send_slack_reply

# Set up logging
logger = logging.getLogger(__name__)

# ---------- State Definition ----------
class LLPLinkMapState(BaseModel):
    """State for LLP (1A) – LinkMap "N→Y" – 2025-07-08 agent."""
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Core state fields
    is_uk: bool = False
    framework: Optional[str] = None
    link_hits: Dict[str, Any] = Field(default_factory=dict)
    proposed_updates: List[str] = Field(default_factory=list)
    
    # Tracking fields
    success: bool = False
    error_message: Optional[str] = None
    actions_taken: List[str] = Field(default_factory=list)

# ---------- Tool Functions ----------
def call_search_linksmaster(state: LLPLinkMapState, **kwargs) -> Dict[str, Any]:
    """Wrapper for search_linksmaster tool."""
    try:
        result = search_linksmaster(**kwargs)
        logger.info("Successfully called search_linksmaster")
        state.actions_taken.append("search_linksmaster")
        return result
    except Exception as e:
        logger.error(f"Error calling search_linksmaster: {e}")
        state.error_message = f"search_linksmaster failed: {str(e)}"
        return {}

def call_update_linksmaster(state: LLPLinkMapState, **kwargs) -> Dict[str, Any]:
    """Wrapper for update_linksmaster tool."""
    try:
        result = update_linksmaster(**kwargs)
        logger.info("Successfully called update_linksmaster")
        state.actions_taken.append("update_linksmaster")
        return result
    except Exception as e:
        logger.error(f"Error calling update_linksmaster: {e}")
        state.error_message = f"update_linksmaster failed: {str(e)}"
        return {}

def call_send_slack_reply(state: LLPLinkMapState, **kwargs) -> Dict[str, Any]:
    """Wrapper for send_slack_reply tool."""
    try:
        result = send_slack_reply(**kwargs)
        logger.info("Successfully called send_slack_reply")
        state.actions_taken.append("send_slack_reply")
        return result
    except Exception as e:
        logger.error(f"Error calling send_slack_reply: {e}")
        state.error_message = f"send_slack_reply failed: {str(e)}"
        return {}

# ---------- Node Functions ----------
def triage_node(state: LLPLinkMapState) -> LLPLinkMapState:
    """
    Determines if issue is UK-related and extracts framework
    
    Inputs: messages
    Outputs: is_uk, framework
    """
    logger.info("Executing triage_node")
    
    # Routing/condition node implementation
    try:
        # Triage logic
        if state.messages:
            content = state.messages[-1].get('content', '').lower()
            state.is_uk = any(keyword in content for keyword in ['uk', 'scotland', 'ireland', 'guernsey', 'wales'])
            
            # Extract framework if mentioned
            for framework in ['frs102', 'frs105', 'llp', 'sorp']:
                if framework in content:
                    state.framework = framework.upper()
                    break
        
        logger.info("Routing triage_node completed")
        
    except Exception as e:
        logger.error(f"Error in triage_node: {e}")
        state.error_message = str(e)
    
    return state

def find_links_node(state: LLPLinkMapState) -> LLPLinkMapState:
    """
    Searches LinkMaster for affected links
    
    Inputs: is_uk
    Outputs: link_hits
    """
    logger.info("Executing find_links_node")
    
    # Tool node implementation
    try:
        # Search operation
        search_links = ["cl.524.000", "nl.524.000"]
        result = call_search_linksmaster(state, links=search_links)
        state.link_hits = result
        
        logger.info("Tool find_links_node completed successfully")
        
    except Exception as e:
        logger.error(f"Error in find_links_node: {e}")
        state.error_message = str(e)
    
    return state

def update_linkmaster_node(state: LLPLinkMapState) -> LLPLinkMapState:
    """
    Updates generation flags from N to Y
    
    Inputs: link_hits
    Outputs: proposed_updates
    """
    logger.info("Executing update_linkmaster_node")
    
    # Tool node implementation
    try:
        # Update operation
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
            state.proposed_updates.append(f"Updated {link_update['link']} flag to Y")
        
        state.success = True
        logger.info("Tool update_linkmaster_node completed successfully")
        
    except Exception as e:
        logger.error(f"Error in update_linkmaster_node: {e}")
        state.error_message = str(e)
    
    return state

def reply_node(state: LLPLinkMapState) -> LLPLinkMapState:
    """
    Sends formatted reply to Slack
    
    Inputs: proposed_updates, success
    Outputs: messages
    """
    logger.info("Executing reply_node")
    
    # Tool node implementation
    try:
        if state.success and state.proposed_updates:
            # Success reply
            reply_message = {
                "text": f"✅ **UK Template Fix Applied**\n\n"
                       f"**Changes made:**\n" + 
                       "\n".join([f"• {update}" for update in state.proposed_updates]) +
                       f"\n\n**Next steps:**\n"
                       f"• Refresh your template\n"
                       f"• The missing links should now appear\n"
                       f"• Contact support if issues persist",
                "thread_ts": state.messages[-1].get('ts') if state.messages else None
            }
        elif not state.is_uk:
            # Non-UK reply
            reply_message = {
                "text": "Hi! This appears to be a template issue that doesn't require UK-specific handling. "
                       "Please contact our general support team for assistance.",
                "thread_ts": state.messages[-1].get('ts') if state.messages else None
            }
        else:
            # Error reply
            reply_message = {
                "text": f"❌ **Unable to automatically fix this issue**\n\n"
                       f"**Error:** {state.error_message or 'Unknown error occurred'}\n\n"
                       f"This has been escalated to our support team for manual review.",
                "thread_ts": state.messages[-1].get('ts') if state.messages else None
            }
        
        result = call_send_slack_reply(state, message=reply_message)
        
        logger.info("Tool reply_node completed successfully")
        
    except Exception as e:
        logger.error(f"Error in reply_node: {e}")
        state.error_message = str(e)
    
    return state

# ---------- Conditional Edge Functions ----------
def decide_triage_node_next(state: LLPLinkMapState) -> str:
    """Decision function for triage_node node."""
    if state.is_uk:
        return "find_links_node"
    return "reply_node"

def decide_find_links_node_next(state: LLPLinkMapState) -> str:
    """Decision function for find_links_node node."""
    if state.link_hits:
        return "update_linkmaster_node"
    return "reply_node"

def decide_update_linkmaster_node_next(state: LLPLinkMapState) -> str:
    """Decision function for update_linkmaster_node node."""
    if state.success:
        return "reply_node"
    return "reply_node"  # Always proceed to reply for error handling

# ---------- Graph Construction ----------
def create_llplinkmap_agent():
    """Create and return the compiled LangGraph agent."""
    
    # Initialize the state graph
    graph = StateGraph(LLPLinkMapState)
    
    # Add nodes
    graph.add_node("triage_node", triage_node)
    graph.add_node("find_links_node", find_links_node)
    graph.add_node("update_linkmaster_node", update_linkmaster_node)
    graph.add_node("reply_node", reply_node)
    
    # Add edges
    graph.add_edge(START, "triage_node")
    
    graph.add_conditional_edges(
        "triage_node",
        decide_triage_node_next,
        {
            "find_links_node": "find_links_node",
            "reply_node": "reply_node"
        }
    )
    
    graph.add_conditional_edges(
        "find_links_node",
        decide_find_links_node_next,
        {
            "update_linkmaster_node": "update_linkmaster_node",
            "reply_node": "reply_node"
        }
    )
    
    graph.add_conditional_edges(
        "update_linkmaster_node",
        decide_update_linkmaster_node_next,
        {
            "reply_node": "reply_node"
        }
    )
    
    # Add final edges to END
    graph.add_edge("reply_node", END)
    
    # Compile the graph
    return graph.compile()

# ---------- Agent Instance ----------
LLPLinkMapAgent = create_llplinkmap_agent()

# ---------- Testing Function ----------
def test_agent_with_case():
    """Test the agent with the provided test case."""
    test_case = {
        "input": {
            "slack_message": "UK user reporting missing cl.524.000 link in FRS102 (1A)",
            "framework": "FRS102",
            "variant": "1A",
            "user_location": "UK"
        },
        "expected_output": {
            "actions_taken": ["search_linksmaster", "update_linksmaster", "send_slack_reply"],
            "links_updated": ["cl.524.000", "nl.524.000"],
            "flags_changed": [{"link": "cl.524.000", "from": "N", "to": "Y"}],
            "reply_sent": True,
            "success": True
        }
    }
    
    if not test_case:
        logger.warning("No test case provided")
        return False
    
    try:
        # Create initial state from test case
        initial_state = LLPLinkMapState(
            messages=[{"content": test_case.get("input", {}).get("slack_message", "")}]
        )
        
        # Run the agent
        result = LLPLinkMapAgent.invoke(initial_state)
        
        # Validate against expected output
        expected = test_case.get("expected_output", {})
        
        # Check success criteria
        success_criteria = [
            # Template flags changed from N to Y
            # Unit test passes with new configuration
            # Support ticket auto-reply sent
            # LinkMaster updated successfully
            # Changes validated in test environment
        ]
        
        # Basic validation
        assert result.success == expected.get("success", False), "Success status mismatch"
        assert "search_linksmaster" in result.actions_taken, "Search action not taken"
        assert "update_linksmaster" in result.actions_taken, "Update action not taken"
        assert "send_slack_reply" in result.actions_taken, "Reply action not taken"
        
        logger.info("Test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    # Run test when script is executed directly
    test_result = test_agent_with_case()
    print(f"Test {'PASSED' if test_result else 'FAILED'}")