# A two-minute portfolio review

This portfolio is relevant to AI implementation, business automation, voice
systems, solutions consulting and CRM/ERP integration roles across companies.
It connects operational experience with practical AI-assisted implementation.

## Start with the result

1. Watch the [short workflow illustration](../assets/workflow.gif), or open its
   [static version](../assets/workflow.png).
2. Read the [case notes](project-cases.md) for the business problem, my
   contribution and the limits of the public evidence.
3. Run `python3 -m portfolio demo` from the repository root. Inspect the
   generated report and [saved example outcomes](../examples/crm-events.json).

The illustration is a conceptual storyboard. The runnable examples use
synthetic inputs and fixture providers. No live API account or private system
is needed to inspect the implementation patterns.

## AI implementation and automation

Relevant work includes n8n/API workflows, structured CRM updates, ERP-connected
business processes, requirements analysis, output validation and troubleshooting.
Inspect [the transactional event pipeline](../portfolio/operations.py),
its [failure tests](../tests/test_operations.py) and the
[n8n validation reference](../n8n/crm-review-workflow.json).

The public CRM example waits for trusted approval, audits rejected input and
prevents an identical event from changing a record twice. It does not publish
a production customer database or claim measured business ROI.

## Voice and conversation systems

Project experience includes Asterisk/SIP/AudioSocket, real-time speech APIs,
transcription, explicit speaker roles, tool calling and provider troubleshooting.
Inspect [voice transport](../portfolio/voice.py),
[call reconstruction](../portfolio/transcript.py),
[voice tests](../tests/test_voice.py) and the
[synthetic transcript](../examples/transcript.txt).

The examples demonstrate packet framing, interruption, fallback and fixture
dialogue processing. The distributed audio is synthetic test tones; there is
no real customer recording or live-provider quality benchmark.

## Solutions, integrations and business operations

I bring over 10 years of management experience in electronic components
distribution, including procurement, logistics, supplier negotiations and
P&L responsibility for a company with annual turnover exceeding $20M.
This is company turnover, not a claim about personal sales or AI-project revenue.

Inspect [architecture and failure boundaries](architecture.md) and the
[business integration case](project-cases.md#business-workflows-and-crmerp-integration).
My contribution combines operational judgement, AI-assisted implementation,
validation, troubleshooting and documentation. The management period is not
presented as years of software engineering or AI consulting.

## Useful interview topics

- How a business requirement becomes an API or n8n workflow.
- How to stop malformed or low-confidence AI output from changing business state.
- How to investigate a duplicate delivery, a speaker-role error or a provider timeout.
- How to explain implementation decisions and agree practical acceptance criteria.

I can discuss anonymised project decisions and a practical assessment.
Contact: bolesusi147@gmail.com. Location: CIS region.
