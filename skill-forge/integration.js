// Skill Forge Integration Layer
// Connects Skill Forge to OpenClaw's existing systems

const { SkillForge } = require('./engine.js');

class ForgeIntegration {
  constructor(openclawInstance) {
    this.forge = new SkillForge();
    this.openclaw = openclawInstance;
    this.skillRegistry = new Map();
    this.executionHistory = [];
  }

  // Register a synthesized capability as a usable skill
  registerSkill(capability) {
    const skill = {
      id: `forge-${capability.name}`,
      name: capability.name,
      source: 'skill-forge',
      synthesized: true,
      implementation: capability.implementation,
      registeredAt: Date.now()
    };
    this.skillRegistry.set(skill.id, skill);
    return skill;
  }

  // Execute a task through the forge
  async runTask(taskDescription, options = {}) {
    console.log(`[Forge] Executing: ${taskDescription}`);
    
    const result = await this.forge.execute(taskDescription, options);
    
    // Register all synthesized capabilities
    for (const cap of result.results) {
      this.registerSkill(cap);
    }
    
    // Record execution
    this.executionHistory.push({
      task: taskDescription,
      result,
      timestamp: Date.now()
    });
    
    return result;
  }

  // Get available skills from forge
  getAvailableSkills() {
    return Array.from(this.skillRegistry.values());
  }

  // Get execution history
  getHistory() {
    return this.executionHistory;
  }

  // Check if a task can be accomplished
  async canAccomplish(task) {
    const plan = await this.forge.decomposer.decompose(task);
    return {
      can: true,
      capabilities: plan.capabilities,
      strategy: plan.strategy,
      estimatedComplexity: plan.capabilities.length
    };
  }
}

// Factory function to create integration
function createForgeIntegration(openclawInstance) {
  return new ForgeIntegration(openclawInstance);
}

module.exports = { ForgeIntegration, createForgeIntegration };