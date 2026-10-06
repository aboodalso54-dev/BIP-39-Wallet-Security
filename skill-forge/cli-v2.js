#!/usr/bin/env node
'use strict';
// Skill Forge v2.0 CLI — Quantum-Inspired Self-Assembly Engine

const { SkillForgeV2, FORGE_VERSION } = require('./engine-v2.js');

const forge = new SkillForgeV2();

function printHeader() {
  console.log(`\n🔥 Skill Forge v${FORGE_VERSION} — Quantum-Inspired Meta-Cognitive Self-Assembly`);
  console.log('═'.repeat(70));
}

function printExecution(result) {
  console.log(`\n📋 Task: ${result.task}`);
  console.log(`🧩 Domain: ${result.plan.domain}`);
  console.log(`⚡ Strategy: ${result.plan.strategy}`);
  console.log(`📦 Capabilities (${result.plan.capabilities.length}): ${result.plan.capabilities.join(', ')}`);

  console.log(`\n🧠 Causal Reasoning:`);
  console.log(`   Confidence: ${(result.causal.confidence * 100).toFixed(0)}%`);
  if (result.causal.risks.length > 0) {
    console.log(`   ⚠️  Risks:`);
    result.causal.risks.forEach(r => {
      console.log(`      - ${r.risk} (${(r.probability * 100).toFixed(0)}%) → ${r.mitigation}`);
    });
  }
  if (result.causal.optimizations.length > 0) {
    console.log(`   🚀 Optimizations:`);
    result.causal.optimizations.forEach(o => {
      console.log(`      - ${o.type}: ${o.reason} → ${o.expectedGain}`);
    });
  }

  console.log(`\n⚛️  Quantum Execution:`);
  console.log(`   Explored ${result.execution.allPaths.length} paths in superposition`);
  result.execution.allPaths.forEach(p => {
    const marker = p.id === result.execution.selectedPath ? ' ← COLLAPSED (best)' : '';
    console.log(`   - ${p.id}: score=${p.score}, duration=${p.duration}ms, success=${p.success}${marker}`);
  });

  console.log(`\n📊 Results:`);
  result.execution.results.forEach(r => {
    const icon = r.status === 'completed' ? '✅' : '❌';
    console.log(`   ${icon} ${r.capability}: ${r.status}`);
    if (r.result) console.log(`      ${JSON.stringify(r.result).slice(0, 200)}`);
  });

  console.log(`\n📈 Learning:`);
  console.log(`   Success: ${result.learning.successRate}`);
  console.log(`   Self-improvements: ${result.learning.improvement.length}`);
  result.learning.improvement.forEach(i => {
    console.log(`      - ${i.type}: ${i.target} = ${i.value}`);
  });

  console.log(`\n⏱️  Total duration: ${result.duration}ms`);
  console.log(`🎯 Overall: ${result.success ? 'SUCCESS' : 'PARTIAL'}`);
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const rest = args.slice(1);

  switch (command) {
    case 'execute':
    case 'run': {
      const task = rest.join(' ');
      if (!task) {
        console.log('Usage: skill-forge-v2 execute "<task description>"');
        process.exit(1);
      }
      printHeader();
      const result = await forge.execute(task);
      printExecution(result);
      break;
    }

    case 'quantum': {
      const task = rest.join(' ');
      if (!task) {
        console.log('Usage: skill-forge-v2 quantum "<task description>"');
        process.exit(1);
      }
      printHeader();
      console.log(`\n⚛️  Quantum Superposition Mode`);
      const { plan, capabilities, result } = await forge.quantum(task);
      console.log(`\n📋 Task: ${task}`);
      console.log(`🧩 Capabilities: ${plan.capabilities.join(', ')}`);
      console.log(`\n⚛️  Explored ${result.allPaths.length} paths:`);
      result.allPaths.forEach(p => {
        const marker = p.id === result.selected ? ' ← BEST' : '';
        console.log(`   - ${p.id}: score=${p.score}, ${p.duration}ms, success=${p.success}${marker}`);
      });
      console.log(`\n📊 Collapsed to: ${result.selected} (${result.mode} mode)`);
      result.results.forEach(r => {
        console.log(`   ${r.status === 'completed' ? '✅' : '❌'} ${r.capability}`);
      });
      break;
    }

    case 'causal':
    case 'reason': {
      const task = rest.join(' ');
      if (!task) {
        console.log('Usage: skill-forge-v2 causal "<task description>"');
        process.exit(1);
      }
      printHeader();
      console.log(`\n🧠 Causal Reasoning Mode`);
      const { plan, reasoning } = await forge.causal(task);
      console.log(`\n📋 Task: ${task}`);
      console.log(`🧩 Capabilities: ${plan.capabilities.join(', ')}`);
      console.log(`\n🎯 Confidence: ${(reasoning.confidence * 100).toFixed(0)}%`);
      console.log(`\n📈 Predicted Effects:`);
      reasoning.predictions.forEach(p => {
        console.log(`   - ${p.capability} → ${p.effect} (${(p.probability * 100).toFixed(0)}%)`);
      });
      if (reasoning.risks.length > 0) {
        console.log(`\n⚠️  Identified Risks:`);
        reasoning.risks.forEach(r => {
          console.log(`   - ${r.capability}: ${r.risk} (${(r.probability * 100).toFixed(0)}%)`);
          console.log(`     Mitigation: ${r.mitigation}`);
        });
      }
      if (reasoning.optimizations.length > 0) {
        console.log(`\n🚀 Optimization Opportunities:`);
        reasoning.optimizations.forEach(o => {
          console.log(`   - ${o.type}: ${o.reason}`);
          console.log(`     Expected: ${o.expectedGain}`);
        });
      }
      break;
    }

    case 'transfer': {
      const [from, to] = rest;
      if (!from || !to) {
        console.log('Usage: skill-forge-v2 transfer <from-domain> <to-domain>');
        console.log('Domains: web-development, data-science, devops, system-admin, security, mobile, game-dev, iot');
        process.exit(1);
      }
      printHeader();
      console.log(`\n🔄 Cross-Domain Transfer: ${from} → ${to}`);
      const result = await forge.transfer('transfer task', from, to);
      console.log(`\n📚 Transferable concepts (${result.transferable.length}):`);
      result.transferable.forEach(c => console.log(`   - ${c}`));
      console.log(`\n📋 Transfer Plan:`);
      result.transferPlan.forEach(t => {
        console.log(`   - ${t.concept}: ${t.adaptation} (confidence: ${(t.confidence * 100).toFixed(0)}%)`);
      });
      console.log(`\n✨ Novelty Score: ${result.novelty}`);
      break;
    }

    case 'improve':
    case 'metrics': {
      printHeader();
      const metrics = await forge.improve();
      console.log(`\n📈 Self-Improvement Metrics`);
      console.log(`   Version: ${metrics.version}`);
      console.log(`   Improvement Level: ${metrics.improvementLevel}/10`);
      console.log(`   Executions: ${metrics.performance.executions}`);
      console.log(`   Success Rate: ${metrics.performance.successRate}`);
      console.log(`   Avg Latency: ${metrics.performance.averageLatencyMs}ms`);
      console.log(`   Quantum Explorations: ${metrics.performance.quantumExplorations}`);
      console.log(`   Patterns Learned: ${metrics.patternsLearned}`);
      console.log(`   Self-Adjustments: ${metrics.selfAdjustments}`);
      console.log(`\n⚙️  Current Thresholds:`);
      Object.entries(metrics.thresholds).forEach(([k, v]) => {
        console.log(`   - ${k}: ${v}`);
      });
      break;
    }

    case 'history': {
      printHeader();
      const history = forge.getHistory();
      console.log(`\n📚 Execution History (${history.length} tasks)`);
      history.forEach((h, i) => {
        const icon = h.success ? '✅' : '⚠️';
        console.log(`   ${i + 1}. ${icon} ${h.task} (${h.duration}ms, ${h.plan.domain})`);
      });
      if (history.length === 0) console.log('   (empty)');
      break;
    }

    case 'version':
      console.log(`Skill Forge v${FORGE_VERSION}`);
      break;

    default:
      console.log(`
🔥 Skill Forge v${FORGE_VERSION} — Quantum-Inspired Meta-Cognitive Self-Assembly Engine

Makes the impossible possible through 6 revolutionary capabilities:
  1. Self-Modifying Code Generation
  2. Quantum Superposition Execution
  3. Causal Reasoning Engine
  4. Cross-Domain Transfer
  5. Recursive Self-Improvement
  6. Distributed Resource Fabric

Usage:
  skill-forge-v2 execute "<task>"       Full pipeline execution
  skill-forge-v2 quantum "<task>"       Quantum superposition exploration
  skill-forge-v2 causal "<task>"        Causal reasoning analysis
  skill-forge-v2 transfer <from> <to>   Cross-domain transfer
  skill-forge-v2 improve                Self-improvement metrics
  skill-forge-v2 history                Execution history
  skill-forge-v2 version                Show version

Examples:
  skill-forge-v2 execute "build a real-time collaborative dashboard"
  skill-forge-v2 quantum "create an AI-powered data pipeline"
  skill-forge-v2 causal "deploy a secure authentication system"
  skill-forge-v2 transfer web-development data-science
`);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
