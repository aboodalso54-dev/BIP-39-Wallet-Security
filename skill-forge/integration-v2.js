'use strict';
// Skill Forge v2.0 — OpenClaw Integration Layer
// Connects the Quantum-Inspired Self-Assembly Engine to OpenClaw's systems

const { SkillForgeV2, FORGE_VERSION } = require('./engine-v2.js');

class ForgeIntegrationV2 {
  constructor(openclawInstance) {
    this.forge = new SkillForgeV2();
    this.openclaw = openclawInstance;
    this.synthesizedSkills = new Map();
    this.executionLog = [];
    this.autoActivate = true;
  }

  // Main entry: run any task through the forge
  async runTask(taskDescription, options = {}) {
    console.log(`[Forge v2] 🔥 Executing: ${taskDescription}`);

    const result = await this.forge.execute(taskDescription, options);

    // Register synthesized capabilities as usable skills
    for (const cap of result.capabilities) {
      this._registerSynthesizedSkill(cap, result.plan.domain);
    }

    // Record execution
    this.executionLog.push({
      task: taskDescription,
      domain: result.plan.domain,
      strategy: result.plan.strategy,
      capabilities: result.plan.capabilities,
      success: result.success,
      duration: result.duration,
      selectedPath: result.execution.selectedPath,
      quantumExplorations: result.execution.quantumExplorations,
      timestamp: Date.now()
    });

    return result;
  }

  // Quantum mode: explore all paths in superposition
  async runQuantum(taskDescription, options = {}) {
    console.log(`[Forge v2] ⚛️ Quantum exploration: ${taskDescription}`);
    const { plan, capabilities, result } = await this.forge.quantum(taskDescription, options);
    return { plan, capabilities, result };
  }

  // Causal mode: reason before executing
  async runCausal(taskDescription) {
    console.log(`[Forge v2] 🧠 Causal reasoning: ${taskDescription}`);
    const { plan, reasoning } = await this.forge.causal(taskDescription);
    return { plan, reasoning };
  }

  // Cross-domain transfer
  async runTransfer(fromDomain, toDomain) {
    console.log(`[Forge v2] 🔄 Transfer: ${fromDomain} → ${toDomain}`);
    const result = await this.forge.transfer('transfer', fromDomain, toDomain);
    return result;
  }

  // Register a synthesized capability as a skill
  _registerSynthesizedSkill(capability, domain) {
    const skill = {
      id: `forge-v2-${capability.name}-${Date.now()}`,
      name: capability.name,
      source: 'skill-forge-v2',
      synthesized: true,
      domain,
      strategy: capability.strategy,
      implementation: capability.implementation,
      registeredAt: Date.now()
    };
    this.synthesizedSkills.set(skill.id, skill);
    return skill;
  }

  // Get all synthesized skills
  getSynthesizedSkills() {
    return Array.from(this.synthesizedSkills.values());
  }

  // Get execution log
  getExecutionLog() {
    return this.executionLog;
  }

  // Check if a task can be accomplished
  async canAccomplish(taskDescription) {
    const plan = await this.forge.decomposer.decompose(taskDescription);
    const causal = await this.forge.causalReasoner.reason(taskDescription, plan);
    return {
      can: true,
      capabilities: plan.capabilities,
      domain: plan.domain,
      strategy: plan.strategy,
      complexity: plan.complexity,
      confidence: causal.confidence,
      risks: causal.risks,
      optimizations: causal.optimizations
    };
  }

  // Self-improvement metrics
  async getMetrics() {
    return this.forge.improve();
  }

  // Auto-activate when task exceeds available capabilities
  shouldAutoActivate(taskDescription, availableSkills) {
    if (!this.autoActivate) return false;
    const plan = this.forge.decomposer.decompose(taskDescription);
    const hasAllSkills = plan.capabilities.every(cap =>
      availableSkills.some(s => s.name === cap || s.id === cap)
    );
    return !hasAllSkills;
  }
}

// Factory
function createForgeIntegrationV2(openclawInstance) {
  return new ForgeIntegrationV2(openclawInstance);
}

module.exports = { ForgeIntegrationV2, createForgeIntegrationV2, FORGE_VERSION };
