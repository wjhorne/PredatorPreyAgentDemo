# Architecture Decision: Query Engine vs MCP

## Question
"Is the query_engine required given we are using LLMs? Shouldn't we use MCP tools instead?"

## Answer: You're Right ✓

The `query_engine.py` was designed as a workaround for natural language parsing in a non-LLM context. With LLMs as the primary interface, **MCP is the better architectural choice**.

## Comparison

### Query Engine Approach ❌ (for LLM use)

**How it works:**
1. User types natural language query
2. `query.sh` passes to `pipeline.py` 
3. `query_engine.py` uses regex to parse the text
4. Parameters extracted and passed to simulation
5. Results returned

**Problems for LLM use:**
- Regex parsing is brittle
- LLM already understands language - why parse?
- No type validation
- Parameter constraints not discovered
- Difficult to extend with new tools

**Example problem:**
```
User: "How many rabbits?"  → Fails (needs timestep)
User: "rabbits at step"    → Fails (incomplete number)
User: "step 50 rabbits"    → Maybe works? (depends on regex)
```

### MCP Tool Approach ✓ (for LLM use)

**How it works:**
1. LLM sees available tools with full schema
2. LLM decides which tool to call with structured parameters
3. Tool validates parameters and runs simulation
4. Structured result returned to LLM
5. LLM interprets and responds to user

**Benefits for LLM use:**
- ✓ Type-safe parameter passing
- ✓ LLM sees exactly what's available
- ✓ Built-in schema validation
- ✓ No parsing errors
- ✓ Natural IDE integration

**Example interaction:**
```
User: "How many rabbits?"
LLM: "I need a timestep. Calling query_population(species='rabbit', timestep=180)"
Result: Structured JSON with population data
LLM responds: "At timestep 180, there are 17058.42 rabbits"
```

## Decision Matrix

| Scenario | Query Engine | MCP | Recommendation |
|----------|--------------|-----|-----------------|
| CLI usage (`./query.sh "..."`) | Works | Not applicable | **Use Query Engine** |
| LLM in IDE (Claude Code) | Works but suboptimal | Works perfectly | **Use MCP** ✓ |
| Automation scripts | Works | Works but overkill | **Use Query Engine** or direct import |
| Extensibility | Hard | Easy | **Use MCP** |
| Type safety | None | Full | **Use MCP** |

## What We Did

We created **both**:

1. **`query_engine.py` + `query.sh`** - Still works for CLI usage
   - Good for: Quick manual queries, backward compatibility, no dependencies
   - Kept because: Some users may still prefer CLI

2. **`mcp_server.py`** - New MCP tool server
   - Good for: LLM IDE integration, type-safe, extensible
   - Recommended for: Any LLM-based usage

## No Redundancy - They Serve Different Purposes

- **Use `query.sh`** when: You're at a terminal, want quick answers, prefer CLI
- **Use MCP tools** when: Working in Claude Code/IDE, want type safety, LLM interface

Think of it like:
- `query.sh` = Swiss Army knife (versatile, always works)
- MCP tools = Proper toolbox (specific tools for specific jobs)

## Why We Didn't Remove Query Engine

1. **Backward compatibility** - Existing scripts/workflows might use it
2. **Offline capability** - Query wrapper works without IDE setup
3. **Simplicity** - For simple CLI use, `./query.sh "..."` is faster than IDE setup
4. **Different use cases** - CI/CD, batch processing, automation scripts still prefer direct invocation

## Migration Path

For existing users/workflows:

```
Legacy: ./query.sh "How many foxes at step 180?"
↓
Modern: Use MCP tools in Claude Code
↓
Direct: from config_builder import ConfigBuilder; config = ConfigBuilder.build_config({...})
```

## Future Considerations

Potential improvements:
- [ ] Remove query_engine if MCP adoption becomes ubiquitous
- [ ] Add more MCP tools as new analysis features develop
- [ ] Create OpenAI GPT Actions from MCP schema
- [ ] Support other MCP clients beyond Claude Code

## Bottom Line

✓ **You were right** - query_engine is technically redundant for pure LLM usage  
✓ **MCP is the better architecture** for LLM-based access  
✓ **We kept both** because they serve different use cases  
✓ **MCP is recommended** for Claude Code / IDE usage  
✓ **Query engine can be deprecated** if/when CLI usage becomes unnecessary

---

## Technical References

- **MCP Spec**: https://modelcontextprotocol.io/
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Query Engine**: See `query_engine.py` for regex-based parsing
- **MCP Server**: See `mcp_server.py` for tool definitions
