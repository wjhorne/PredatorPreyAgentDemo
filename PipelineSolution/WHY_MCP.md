# Why We Created MCP Tools (Your Suggestion Was Right)

## Your Question
"Is the query_engine required given we are using LLMs for this? Shouldn't we be able to create things like MCP tools and the LLM can access them to query instead?"

## Answer
**Yes, absolutely correct.** We've now created `mcp_server.py` with proper MCP tools. Here's why this is the better architecture:

## The Problem with Query Engine

The `query_engine.py` with regex-based parsing is fundamentally misaligned with LLM capabilities:

```python
# Old approach (query_engine.py)
patterns = {
    "nt": [
        r"(?:nt|steps|time\s+steps)\s*[:=]\s*(\d+)",
        r"(?:for|Simulate\s+for)?\s*(\d+)\s+(?:steps|time\s+steps?)",
    ],
    "seed": [
        r"seed\s*[:=]\s*(\d+)",
        r"(?:seed|with\s+seed)\s+(\d+)",
    ],
    # ... more fragile regexes
}
```

**Why this is wrong for LLM usage:**
- LLMs are already expert at natural language
- Regex parsing can't handle all phrasing variations
- No type validation
- Parameter constraints not discoverable by LLM
- Doesn't scale as features grow

## The Solution: MCP Tools

```python
# New approach (mcp_server.py)
Tool(
    name="query_population",
    description="Query population at a specific timestep",
    inputSchema={
        "type": "object",
        "properties": {
            "species": {
                "type": "string",
                "enum": ["rabbit", "fox", "both"],
                "description": "Which species to query",
            },
            "timestep": {
                "type": "integer",
                "description": "Timestep to query (0-360)",
            },
        },
        "required": ["species", "timestep"],
    },
)
```

**Why this is better:**
- ✓ LLM sees exact parameters needed
- ✓ Type validation built-in
- ✓ No parsing errors possible
- ✓ Extensible with new tools
- ✓ Native IDE integration

## What We Now Have

### Files Added
1. **`mcp_server.py`** - MCP server exposing 5 tools:
   - `query_population` - Get values at timestep
   - `run_simulation` - Full simulation
   - `generate_report` - Text/PDF output
   - `validate_baseline` - Check against golden run
   - `get_default_parameters` - Show defaults

2. **`MCP_INTEGRATION.md`** - Complete MCP setup guide

3. **`ARCHITECTURE_DECISION.md`** - Detailed explanation of tradeoffs

4. **`claude_config.json`** - Configuration for Claude Code

### Files Kept (Still Useful)
- `query_engine.py` + `query.sh` - For CLI usage, backward compatibility

## Usage Comparison

### Before (Query Engine)
```bash
$ ./query.sh "How many foxes at step 180?"
# Regex tries to parse this, might miss variations
```

### Now (MCP - Recommended)
```
User: "How many foxes at step 180?"
↓
Claude/Gemini sees: query_population tool
  - species: enum ["rabbit", "fox", "both"]
  - timestep: integer
↓
LLM calls: query_population(species="fox", timestep=180)
↓
Result: Structured JSON {"timestep": 180, "fox": 1530.37}
```

## When to Use What

| Context | Use | Why |
|---------|-----|-----|
| Claude Code IDE | **MCP Tools** ✓ | Type-safe, integrated |
| Terminal/CLI | `query.sh` ✓ | Simple, no setup |
| Automation/CI | Direct Python | Fastest, no overhead |
| Testing | Unit tests | Most reliable |

## Bottom Line

Your suggestion was **architecturally sound**. We've now provided:

1. ✓ **MCP tools** as the primary LLM interface
2. ✓ **Query engine** for backward compatibility and CLI
3. ✓ **Documentation** explaining the tradeoff
4. ✓ **Configuration** for easy IDE setup

The system is now designed properly for LLM usage.
