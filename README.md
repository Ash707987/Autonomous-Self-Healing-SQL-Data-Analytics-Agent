🧠 Autonomous Self-Healing SQL Agent

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/c52645c4-367b-46c6-a7fa-4a307e62f120" />


📖 Executive Summary & Theoretical Abstract

In classical software engineering, data retrieval pipelines are strictly linear and deterministic. However, when introducing Large Language Models (LLMs) into data engineering workflows, their probabilistic nature inherently introduces syntax errors, schema hallucinations, and logic failures.

This project implements a Cyclic State Machine (via LangGraph) to construct an Autonomous Self-Healing Agent. Instead of failing on the first database error, the agent acts as an autonomous control loop: it generates SQL, executes it within a deterministic sandbox, analyzes any resulting tracebacks (Root Cause Analysis), and rewrites its own code until execution succeeds.

🏗️ System Architecture: Directed Cyclic Graph (DCG)

The agent operates on a Directed Cyclic Graph (DCG) where the execution state is passed sequentially across specialized cognitive nodes.

graph TD
    A[User Natural Language Query] --> B(Node 1: Retrieve Schema)
    B --> C(Node 2: Generate SQL)
    C --> D(Node 3: Execute SQL Sandbox)
    
    D -->|Execution Success| F(Node 5: Narrate Results)
    D -->|Execution Error / Traceback| E{Conditional Router}
    
    E -->|Retries < 3| G(Node 4: Critique & Fix)
    G -->|Inject Corrected SQL| D
    
    E -->|Retries >= 3| F
    F --> H[Final Executive Summary]
    
    style D fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#ffb3ba,stroke:#333,stroke-width:2px


🧠 The Feedback Control Loop

The core innovation is the feedback loop between Node 3 and Node 4.

Probabilistic Generation: The LLM generates code based on semantic intent.

Deterministic Execution: The SQL engine attempts to compile and run the code. If it violates schema constraints, it throws an exact error string (e.g., OperationalError: no such column).

Cognitive Correction: The Critique node ingests the failure state, compares it to the ground-truth schema, and patches the logic.

📂 File Anatomy & Module Separation

This project strictly adheres to separation of concerns, isolating memory state, execution, and generative logic.

Module

Core Responsibility

Architectural Concept

state.py

Global Memory Lineage

Immutable State Passing. Defines the TypedDict schema passed between nodes.

database.py

The Execution Sandbox

Deterministic Execution. Provides isolated schema reflection and safe try/except execution boundaries.

nodes.py

Cognitive Processing

Specialist Agents. Houses the isolated prompts for generation, debugging, and synthesis.

graph.py

Control Flow Engine

State Machine Assembly. Compiles the nodes and defines the cyclic conditional edges.

main.py

Orchestration

Harness. The execution entry point for testing and visualization.

🚀 Quickstart Guide

Follow these steps to initialize the environment and run the autonomous agent.

1. Initialize the Environment

Use a virtual environment to avoid dependency conflicts.

# Create and activate environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt


2. Configure Environment Variables

Create a .env file in the root directory and inject your OpenAI secret key.

# .env
OPENAI_API_KEY=sk-your-actual-api-key-here


3. Execute the Engine

Run the main script to initialize the SQLite database and watch the agent resolve complex, adversarial queries.

python main.py


🔬 Next Steps: MLOps & Production Scaling

To transition this from a local sandbox to an enterprise-grade microservice, the following MLOps implementations are recommended:

Dynamic RAG (Retrieval-Augmented Generation): Replace static get_schema() with a pgvector store to scale to databases with 1,000+ tables.

LLM Evals (CI/CD): Integrate the ragas library to calculate Answer Faithfulness and Execution Accuracy against a golden dataset prior to prompt merges.

Tracing: Implement LangSmith to record exact token consumption, execution latencies, and self-healing loop trajectories.
