# Agent Lot Sizing

A natural-language production-planning prototype that connects a local language model to deterministic Gurobi lot-sizing tools. The solver, rather than the language model, calculates production quantities, inventory, setups and cost.

## What is implemented

- Single-item, deterministic mixed-integer models with fixed setup, production and inventory costs; no backorders.
- An **uncapacitated** tool in `tools/lot_sizing_tool.py` and a separate **capacitated** tool in `tools/capacitated_lot_sizing_tool.py`.
- `agent.py`: a scripted query through SmolAgents and Phi-3; `agent2.py`: a Streamlit chat interface exposing both tool variants.

Flow: user query → SmolAgents `CodeAgent` → structured solver arguments → Gurobi MILP → plan and cost. Solver calls can also run directly, without downloading a language model.

## Run the solver first

Use Python 3.10+ and a valid Gurobi license. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install gurobipy==12.0.2 smolagents==1.20.0
python tools/lot_sizing_tool.py < examples/sample_query.txt
```

The example file is JSON for the uncapacitated CLI. For capacity limits, use the other tool:

```bash
printf '%s\n' '{"demand":[5,5],"capacity":[5,5],"setup_cost":10,"unit_cost":2,"holding_cost":1}' | python tools/capacitated_lot_sizing_tool.py
```

This small capacity example produces `[5, 5]`, zero ending inventories, two setups and total cost `40`. The same data without capacity can batch `[10, 0]` for total cost `35`.

## Optional agent interface

```bash
pip install -r requirements.txt
streamlit run agent2.py
```

The configured `microsoft/Phi-3-mini-128k-instruct` model requires a first-use download and sufficient memory. `llama-cpp-python` in the requirements is an optional backend and may need native build tools. Review generated code and use an isolated environment: `CodeAgent` executes generated Python.

## Validation and limits

```bash
python -m unittest discover -s tests -v
```

Six local regressions passed with Python 3.11 / Gurobi 12.0.2: batching versus holding cost, initial inventory, binding capacity, infeasibility and mismatched capacity lengths. Tests recompute cost and inventory balance from the returned decisions. The explicit `.values()` sums avoid Gurobi's deprecated tupledict summation interface; the previous interface was verified to give the same objective in this version.

The LLM/Streamlit path was not exercised in that check. This is a prototype, with no benchmark of agent accuracy, runtime scaling or production deployment. Inputs should use finite, nonnegative demand, costs and stock; input validation is incomplete. It does not model multiple items or perishability. No project-wide license is declared.
