# MCP Integration Guide

## Why MCP is Better Than Query Parsing

The original architecture used `query_engine.py` with regex-based natural language parsing. This approach has limitations when used with LLMs:

- **Query parsing is fragile**: Regex patterns can miss variations or misinterpret queries
- **Redundant NLP**: LLMs are already excellent at understanding natural language
- **Type safety**: Tools don't have schema validation
- **Discoverability**: Users/LLMs must guess what queries work

**MCP (Model Context Protocol) is the solution**: Instead of parsing text, expose well-defined tools that the LLM can invoke directly with structured parameters.

## Architecture: MCP vs Query Engine

### Query Engine Approach (Original)
```
User Query (text)
    ↓
query.sh wrapper
    ↓
query_engine.py (regex parsing)
    ↓
pipeline.py
    ↓
Simulation Result
```

**Pros**: Works for CLI usage
**Cons**: Fragile parsing, doesn't scale well with LLMs

### MCP Tool Approach (Better for LLMs)
```
LLM (Claude, Gemini, etc.)
    ↓
MCP Client (in IDE)
    ↓
mcp_server.py (tool definitions + implementations)
    ↓
Simulation functions
    ↓
Structured result
```

**Pros**: Type-safe, discoverable, LLM-native, no parsing needed
**Cons**: Requires MCP-compatible client (Claude Code, etc.)

## Using the MCP Server

### Setup

1. Install MCP package:
   ```bash
   pip install -r requirements.txt  # includes mcp==0.1.0
   ```

2. Configure your IDE to use the MCP server:

   **Claude Code / Claude in VS Code**:
   - Add to `.claude/config.json` (or use provided `claude_config.json`):
     ```json
     {
       "mcpServers": {
         "predator-prey-simulation": {
           "command": "python",
           "args": ["mcp_server.py"],
           "cwd": "${workspaceFolder}/PipelineSolution"
         }
       }
     }
     ```
   - Restart VS Code to load the MCP server

   **Cursor**:
   - Open settings: `Ctrl+,` (or `Cmd+,` on Mac)
   - Search for "MCP"
   - In cursor settings JSON, add:
     ```json
     "mcpServers": {
       "predator-prey-simulation": {
         "command": "python",
         "args": ["mcp_server.py"],
         "cwd": "${workspaceFolder}/PipelineSolution"
       }
     }
     ```
   - Restart Cursor

   **Google Gemini (Web/API)**:
   - Currently, Gemini web interface doesn't support direct MCP connection
   - **Workaround 1 (Recommended)**: Use Gemini Code Execution
     1. In Gemini chat, provide the setup code:
        ```bash
        cd /path/to/PipelineSolution
        python3 -m venv .venv
        source .venv/bin/activate  # or .venv\Scripts\activate on Windows
        pip install -r requirements.txt
        ```
     2. Ask Gemini to help you call the tools directly via Python:
        ```python
        from config_builder import ConfigBuilder
        from simulation_runner import SimulationRunner
        # Gemini can now call these functions directly
        ```
     3. This gives Gemini direct access to the simulation without MCP protocol
   
   - **Workaround 2 (Advanced)**: Create Gemini Custom Tool
     1. Export the MCP schema as JSON (can be extracted from `mcp_server.py`)
     2. Go to [Google AI Studio](https://aistudio.google.com)
     3. Create a new project and add a "Custom Tool"
     4. Provide the tool definitions with parameters and descriptions
     5. Reference from Gemini chat:
        ```
        User: "Query the predator-prey simulation..."
        Gemini: [Uses custom tool with structured parameters]
        ```

   **OpenAI Codex / ChatGPT Code Interpreter**:
   - Currently, ChatGPT doesn't support direct MCP connection
   - **Workaround 1 (Recommended)**: Use Code Interpreter
     1. In ChatGPT Code Interpreter, upload the PipelineSolution folder
     2. Ask ChatGPT to set up and run:
        ```python
        import os
        os.chdir('/tmp/uploaded_files/PipelineSolution')  # or wherever uploaded
        
        # Add to path
        import sys
        sys.path.insert(0, '.')
        
        # Now import and use directly
        from config_builder import ConfigBuilder
        from simulation_runner import SimulationRunner
        from validation import BaselineValidator
        from report_generator import TextReportGenerator, PDFReportGenerator
        
        # ChatGPT can now call these functions with parameters
        ```
     3. ChatGPT can then make queries like:
        ```
        User: "Show me the fox population at step 180"
        ChatGPT: [Uses Code Interpreter to run] → Returns result
        ```
   
   - **Workaround 2 (Custom GPT via Function Calling)**:
     1. Create a custom GPT at https://chat.openai.com/gpts/editor
     2. Click "Create new action"
     3. Extract OpenAPI schema from tool definitions
     4. Configure schema with the 5 tools (query_population, run_simulation, etc.)
     5. Example schema snippet:
        ```json
        {
          "openapi": "3.0.0",
          "info": {"title": "Predator-Prey Simulation", "version": "1.0.0"},
          "paths": {
            "/query_population": {
              "post": {
                "summary": "Query population at timestep",
                "parameters": [
                  {"name": "species", "schema": {"type": "string", "enum": ["rabbit", "fox", "both"]}},
                  {"name": "timestep", "schema": {"type": "integer"}}
                ]
              }
            }
          }
        }
        ```
     6. Publish the GPT and share with others

3. After configuration, restart your IDE/reload the tool to load the MCP server

### Available Tools

Once configured, you can ask the LLM to call these tools:

#### 1. `query_population`
Get population at a specific timestep.

```
Parameters:
  - species (required): "rabbit", "fox", or "both"
  - timestep (required): integer 0-360
  - nx (optional): grid width, default 50
  - ny (optional): grid height, default 50
  - nt (optional): total steps, default 360
  - seed (optional): random seed, default 12345

Example: "How many foxes at step 180?"
→ Calls: query_population(species="fox", timestep=180)
→ Result: "Foxes: 1530.37"
```

#### 2. `run_simulation`
Run a simulation and get statistics.

```
Parameters:
  - All simulation parameters (nx, ny, nt, seed, etc.)
  - All optional with sensible defaults

Example: "Run a simulation with a 30x30 grid"
→ Calls: run_simulation(nx=30, ny=30)
→ Result: Population statistics in JSON format
```

#### 3. `generate_report`
Generate text or PDF report.

```
Parameters:
  - format (required): "text" or "pdf"
  - output_file (optional): file path to save
  - All simulation parameters (optional)

Example: "Generate a PDF report"
→ Calls: generate_report(format="pdf")
→ Result: "✓ PDF report generated: report_20260422_124500.pdf"
```

#### 4. `validate_baseline`
Validate against the golden hand-run example.

```
Parameters:
  - seed (optional): default 12345

Example: "Does this match the baseline?"
→ Calls: validate_baseline()
→ Result: "✓ PASSED: exact match within tolerance"
```

#### 5. `get_default_parameters`
Show all default configuration parameters.

```
Example: "What are the default parameters?"
→ Calls: get_default_parameters()
→ Result: JSON with all defaults
```

## Example Interactions with LLM

### Example 1: Population Query
```
User: "How many foxes are there at step 180?"

LLM decides to call:
  query_population(species="fox", timestep=180)

Result:
  Population at timestep 180:
  - Foxes: 1530.37
```

### Example 2: Parameter Sweep
```
User: "Run simulations with 3 different grid sizes and show me how they differ"

LLM calls:
  1. run_simulation(nx=30, ny=30)
  2. run_simulation(nx=50, ny=50)
  3. run_simulation(nx=70, ny=70)

Result:
  [Comparison of statistics from all three]
```

### Example 3: Report Generation
```
User: "Create a PDF report showing what happens with high fox mortality"

LLM calls:
  run_simulation(fox_mortality=0.95)  # Get the data
  generate_report(format="pdf", output_file="high_mortality.pdf")

Result:
  ✓ PDF report generated: high_mortality.pdf
```

## When to Use What

| Use Case | Tool | Why |
|----------|------|-----|
| CLI queries | `query.sh` | Simple, no dependencies |
| Claude Code / Cursor IDE | MCP tools | Native, type-safe, discoverable |
| Gemini Code Execution | Direct Python import | Code Interpreter method |
| ChatGPT Code Interpreter | Direct Python import | Upload folder and run directly |
| ChatGPT Custom GPT | OpenAPI schema | Reusable GPT action |
| Automation scripts | Direct Python import | Fastest, no overhead |
| Manual exploration | Any works | Choose based on preference |

## Migration from Query Engine

The old `query_engine.py` and `query.sh` still work for backward compatibility, but for LLM usage, MCP is preferred:

- ✗ Don't rely on `query_engine.py` for new LLM integrations
- ✓ Use `mcp_server.py` for LLM-based access
- ✓ Keep `query.sh` for CLI usage

## Technical Notes

- MCP server runs in-process with the LLM client (fast, no network)
- All tools are async-ready for concurrent calls
- Errors are caught and returned as tool results (not exceptions)
- Parameters are validated before simulation runs
- Results are structured (JSON) for parsing

## Troubleshooting

**"No tools available"**
- Ensure `mcp_server.py` is in the PipelineSolution directory
- Check that MCP package is installed: `pip install mcp`
- Restart your IDE after configuring MCP

**"Tool execution timed out"**
- Large simulations (nx=100, nt=1000) take time
- MCP has default 30s timeout - may need configuration
- Try smaller grids first

**"Parameter validation failed"**
- Check that all parameters are in valid ranges
- Negative grids, negative seeds, zero timesteps will fail
- LLM should ask for clarification if invalid

## Future Enhancements

Possible additions to MCP server:
- Parameter suggestions based on desired behavior
- Automated parameter sweeps
- Comparison tools between runs
- Export/visualization helpers
- Integration with analysis workflows
