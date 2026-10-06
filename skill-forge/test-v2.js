#!/usr/bin/env node
'use strict';
// Skill Forge v2.0 — Self-Test Suite

const { SkillForgeV2, FORGE_VERSION } = require('./engine-v2.js');

let passed = 0;
let failed = 0;

async function test(name, fn) {
  try {
    await fn();
    console.log(`✅ ${name}`);
    passed++;
  } catch (err) {
    console.log(`❌ ${name}: ${err.message}`);
    failed++;
  }
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg || 'Assertion failed');
}

async function main() {
  console.log(`\n🔥 Skill Forge v${FORGE_VERSION} — Self-Test Suite`);
  console.log('═'.repeat(50));

  const forge = new SkillForgeV2();

  await test('Engine instantiates', () => {
    assert(forge.version === FORGE_VERSION);
    assert(forge.decomposer);
    assert(forge.synthesizer);
    assert(forge.causalReasoner);
    assert(forge.quantumExecutor);
    assert(forge.resourceFabric);
    assert(forge.domainTransfer);
    assert(forge.metaLearner);
  });

  await test('Task decomposition', async () => {
    const plan = await forge.decomposer.decompose('build a real-time data dashboard');
    assert(plan.capabilities.length > 0, 'No capabilities extracted');
    assert(plan.domain, 'No domain detected');
    assert(plan.strategy, 'No strategy determined');
    console.log(`   Capabilities: ${plan.capabilities.join(', ')}`);
    console.log(`   Domain: ${plan.domain}, Strategy: ${plan.strategy}`);
  });

  await test('Capability synthesis', async () => {
    const plan = await forge.decomposer.decompose('create a web API');
    const caps = await forge.synthesizer.synthesize(plan);
    assert(caps.length > 0, 'No capabilities synthesized');
    assert(caps.every(c => c.implementation?.code), 'Missing generated code');
  });

  await test('Causal reasoning', async () => {
    const plan = await forge.decomposer.decompose('fetch data from API and process it');
    const reasoning = await forge.causalReasoner.reason('fetch data', plan);
    assert(reasoning.confidence > 0, 'No confidence score');
    assert(Array.isArray(reasoning.predictions), 'No predictions');
    assert(Array.isArray(reasoning.risks), 'No risks');
    assert(Array.isArray(reasoning.optimizations), 'No optimizations');
  });

  await test('Quantum superposition execution', async () => {
    const plan = await forge.decomposer.decompose('build a data pipeline');
    const caps = await forge.synthesizer.synthesize(plan);
    const result = await forge.quantumExecutor.explore('test', caps, { timeout: 3000 });
    assert(result.selected, 'No selected path');
    assert(result.allPaths.length >= 2, 'Insufficient exploration paths');
    console.log(`   Explored ${result.allPaths.length} paths, selected: ${result.selected}`);
  });

  await test('Full execution pipeline', async () => {
    const result = await forge.execute('create a data processing pipeline');
    assert(result.id, 'No execution ID');
    assert(result.plan, 'No plan');
    assert(result.execution, 'No execution results');
    assert(typeof result.duration === 'number', 'No duration');
    console.log(`   Duration: ${result.duration}ms, Success: ${result.success}`);
  });

  await test('Cross-domain transfer', async () => {
    const result = await forge.transfer('task', 'web-development', 'data-science');
    assert(result.fromDomain === 'web-development');
    assert(result.toDomain === 'data-science');
    assert(Array.isArray(result.transferPlan));
    console.log(`   Transferable concepts: ${result.transferable.length}`);
  });

  await test('Meta-learning & self-improvement', async () => {
    const metrics = await forge.improve();
    assert(metrics.performance.executions > 0, 'No executions recorded');
    assert(metrics.patternsLearned >= 0);
    assert(metrics.improvementLevel >= 1);
    console.log(`   Executions: ${metrics.performance.executions}, Level: ${metrics.improvementLevel}`);
  });

  await test('Resource fabric capacity', () => {
    const capacity = forge.resourceFabric.getCapacity();
    assert(capacity.cpuCores > 0, 'No CPU cores detected');
    assert(capacity.totalMemoryMB > 0, 'No memory detected');
    console.log(`   CPU cores: ${capacity.cpuCores}, Memory: ${capacity.totalMemoryMB}MB`);
  });

  await test('Code generation executes', async () => {
    const plan = await forge.decomposer.decompose('create a user interface');
    const caps = await forge.synthesizer.synthesize(plan);
    const uiCap = caps.find(c => c.name === 'user-interface');
    assert(uiCap, 'UI capability not synthesized');
    const code = uiCap.implementation.code;
    assert(code.includes('generateUI'), 'Generated code missing function');
    const result = await forge.quantumExecutor._safeExecute(code, 3000);
    assert(result, 'Generated code did not execute');
    console.log(`   Generated UI: ${JSON.stringify(result).slice(0, 100)}`);
  });

  console.log('\n' + '═'.repeat(50));
  console.log(`📊 Results: ${passed} passed, ${failed} failed`);
  console.log(failed === 0 ? '🎉 ALL TESTS PASSED' : '⚠️  SOME TESTS FAILED');
  process.exit(failed === 0 ? 0 : 1);
}

main().catch(err => {
  console.error('Test suite error:', err);
  process.exit(1);
});
