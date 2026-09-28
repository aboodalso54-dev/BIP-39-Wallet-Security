#!/usr/bin/env node
// Skill Forge CLI - Makes the impossible possible

const { SkillForge } = require('./engine.js');
const { ForgeIntegration } = require('./integration.js');

const forge = new SkillForge();
const integration = new ForgeIntegration(null);

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const task = args.slice(1).join(' ');

  switch (command) {
    case 'execute':
    case 'run':
      if (!task) {
        console.log('Usage: skill-forge execute "<task description>"');
        process.exit(1);
      }
      console.log(`🔥 Skill Forge: "${task}"`);
      console.log('─'.repeat(50));
      
      const result = await integration.runTask(task);
      
      console.log('\n✅ Execution Complete');
      console.log(`   Version: ${result.version}`);
      console.log(`   Capabilities: ${result.results.length}`);
      result.results.forEach((r, i) => {
        console.log(`   ${i + 1}. ${r.capability} → ${r.strategy} → ${r.status}`);
      });
      break;

    case 'analyze':
    case 'check':
      if (!task) {
        console.log('Usage: skill-forge analyze "<task description>"');
        process.exit(1);
      }
      const analysis = await integration.canAccomplish(task);
      console.log(`\n🔍 Analysis: "${task}"`);
      console.log(`   Can accomplish: ${analysis.can}`);
      console.log(`   Strategy: ${analysis.strategy}`);
      console.log(`   Required capabilities: ${analysis.capabilities.join(', ')}`);
      console.log(`   Complexity: ${analysis.estimatedComplexity}/10`);
      break;

    case 'skills':
      const skills = integration.getAvailableSkills();
      console.log('\n📦 Synthesized Skills:');
      skills.forEach(s => {
        console.log(`   - ${s.name} (source: ${s.source})`);
      });
      if (skills.length === 0) console.log('   (none yet)');
      break;

    case 'history':
      const history = integration.getHistory();
      console.log('\n📚 Execution History:');
      history.forEach(h => {
        console.log(`   - ${h.task} (${new Date(h.timestamp).toLocaleString()})`);
      });
      if (history.length === 0) console.log('   (empty)');
      break;

    case 'version':
      console.log(`Skill Forge v${require('./engine.js').FORGE_VERSION}`);
      break;

    default:
      console.log(`
🔥 Skill Forge - Meta-Cognitive Self-Assembly Engine

Usage:
  skill-forge execute "<task>"     Execute a task through the forge
  skill-forge analyze "<task>"     Analyze what a task requires
  skill-forge skills              List synthesized skills
  skill-forge history             Show execution history
  skill-forge version             Show version

Examples:
  skill-forge execute "build a real-time chat app"
  skill-forge analyze "create a data visualization dashboard"
`);
  }
}

main().catch(console.error);