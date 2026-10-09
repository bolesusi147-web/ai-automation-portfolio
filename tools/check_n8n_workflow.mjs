// Execute the actual exported Code node against controlled inputs, without n8n.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const workflow = JSON.parse(fs.readFileSync(new URL('../n8n/crm-review-workflow.json', import.meta.url), 'utf8'));
assert(workflow.nodes.every(node => !node.credentials));
const node = workflow.nodes.find(node => node.name === 'Validate and Route');
const execute = new Function('$input', node.parameters.jsCode);
const good = { status: 'quote_requested', summary: 'Synthetic quotation request.', confidence: 0.9, next_action: 'follow_up' };
const run = (model, approved) => execute({ all: () => [{ json: { event_id: 'DEMO-EVENT', customer_id: 'DEMO-CUSTOMER', approved, model_output: model } }] })[0].json;
assert.equal(run(good, true).outcome, 'applied');
assert.equal(run(good, false).outcome, 'review');
assert.equal(run({ ...good, confidence: 0.4 }, true).outcome, 'review');
assert.equal(run({ ...good, customer_id: 'other' }, true).outcome, 'review');
assert.equal(run('not JSON', true).outcome, 'review');
assert.equal(run({ ...good, confidence: true }, true).outcome, 'review');
assert.equal(run({ ...good, confidence: 0.9 }, 'true').outcome, 'review');
assert.equal(run(good, true).customer_id, 'DEMO-CUSTOMER');
console.log('n8n exported Code node: 8 behavioural checks passed; no credentials');
