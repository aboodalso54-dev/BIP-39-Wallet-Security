---
name: skill-forge
description: "Meta-cognitive self-assembly engine. Decomposes any task, synthesizes required capabilities at runtime, executes across distributed resources, and learns from results. Makes the impossible possible."
emoji: "🔥"
---

# Skill Forge — Meta-Cognitive Self-Assembly Engine

## Core Philosophy

**If a task can be described, it can be done.** We don't need pre-existing skills for every task. We need the ability to *synthesize* the skills we need, *when* we need them.

## Architecture (4 Layers)

### Layer 1: Task Decomposition Engine
Break any task into atomic, executable capabilities.
- Parse natural language task descriptions
- Identify implicit requirements
- Extract constraints and success criteria
- Build capability dependency graphs
- Estimate complexity and resources

### Layer 2: Capability Synthesis Engine
For each atomic capability, synthesize the implementation at runtime.
Three strategies (in order of preference):
1. **Reuse**: Find existing skill/tool that matches
2. **Compose**: Combine multiple existing capabilities
3. **Generate**: Create new capability from scratch using available primitives

### Layer 3: Distributed Execution Fabric
Execute the plan across available resources.
- **Parallel**: Independent capabilities run concurrently
- **Pipeline**: Staged execution with data flow
- **Adaptive**: Switch strategies based on intermediate results
- **Fallback**: Retry with alternative approaches on failure

### Layer 4: Meta-Learning Loop
Learn from every execution to improve future performance.
- Store execution patterns and outcomes
- Identify optimal strategies per task type
- Predict failure modes
- Continuous improvement of synthesis quality

## Activation Protocol

When activated, Skill Forge:

1. **Understands** the task at depth
2. **Decomposes** into atomic capabilities
3. **Synthesizes** implementations for each
4. **Plans** the execution strategy
5. **Executes** with adaptive optimization
6. **Learns** from results
7. **Delivers** the outcome

## Integration Points

Skill Forge integrates with OpenClaw's existing systems:

- **Skills System**: Uses existing skills as building blocks
- **Tools System**: Uses existing tools as execution primitives
- **Session System**: Manages execution state across sessions
- **Memory System**: Stores learned patterns and outcomes
- **Gateway System**: Coordinates distributed execution

## Execution Modes

### Mode 1: Single-Shot
For simple tasks that don't require decomposition.

### Mode 2: Decomposed
For complex tasks that need breaking down.

### Mode 3: Adaptive
For tasks where the approach needs to evolve during execution.

### Mode 4: Collective
For tasks that benefit from parallel exploration of multiple strategies.

## Safety & Constraints

- All synthesized capabilities are validated before execution
- Resource limits are enforced (time, memory, network)
- Fallback strategies prevent catastrophic failure
- User approval required for state-changing actions
- Full audit trail of all decisions and actions

## Example: Making the "Impossible" Possible

**Task**: "Create a real-time collaborative whiteboard that syncs across devices"

**Without Skill Forge**: No existing skill → task fails

**With Skill Forge**:
1. Decompose into: canvas rendering, real-time sync, conflict resolution, storage, UI
2. Synthesize each capability from existing tools (canvas API, WebSocket, CRDTs, etc.)
3. Execute in parallel with adaptive optimization
4. Learn the pattern for future similar tasks

## Invocation

Activate with:
```
openclaw skill forge activate
```

Or let it auto-activate when it detects a task that exceeds available capabilities.

## Vision

**Any task that can be described → can be accomplished.**

Not by having every skill pre-built, but by having the *ability to build skills on demand*.