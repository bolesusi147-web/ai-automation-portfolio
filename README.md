# Alex Sparrow · AI & Business Automation

[![Portfolio checks](https://github.com/bolesusi147-web/ai-automation-portfolio/actions/workflows/checks.yml/badge.svg)](https://github.com/bolesusi147-web/ai-automation-portfolio/actions/workflows/checks.yml)

**Practical AI implementation, voice workflows and reliable business integrations.**

I combine over 10 years of management experience in electronic components
distribution with AI-assisted implementation across CRM/ERP, call transcription
and conversational voice agents. My work connects business requirements,
integration, validation, troubleshooting and ongoing support.

This portfolio contains **independent, runnable demonstrations** of those patterns.
All inputs are synthetic. It does not expose customer information or private
business systems. Code here was prepared with AI assistance and reviewed/tested;
it is a demonstration of implementation judgement, not a claim of a conventional
senior software-engineering career.

**Hiring for automation? Start with [the ElevenLabs role guide](docs/elevenlabs.md).**

## Run in two minutes

Python **3.11+**, standard library only. No accounts, API keys or paid services.

```bash
git clone https://github.com/bolesusi147-web/ai-automation-portfolio.git
cd ai-automation-portfolio
python3 -m portfolio demo
python3 -m unittest discover -s tests -v
python3 tools/check_public_content.py
```

The demo creates `.demo-output/`: a JSON report, readable transcript, voice event
trace, CRM audit database and synthetic stereo test tones. Existing output is
never overwritten; use `--output .demo-output/another-run` for another run.
**The tones are transport-test signals, not generated speech.** Transcripts and
model responses are fixtures, not output from a live STT or LLM API.

## Three demonstrations

| Demonstration | What to review | Business relevance |
|---|---|---|
| [Voice agent transport](portfolio/voice.py) | TCP fragmentation, bounded PCM frames, interruption, timeout/fallback, read-only tool calling | Connect telephony to an assistant while controlling stale playback and failure paths |
| [Call-to-dialogue processing](portfolio/transcript.py) | Stereo separation, timestamps, explicit speaker mapping, weaker overlapping echo suppression | Turn a conversation into a usable, attributable record |
| [AI output → CRM](portfolio/operations.py) | Strict schema, human approval, low-confidence review, SQLite transactions, retry/idempotency audit | Keep model mistakes and duplicate deliveries from changing business state |

```mermaid
flowchart LR
    A[Synthetic event or call] --> B[Normalise input]
    B --> C[Fixture provider response]
    C --> D[Validate output]
    D --> E{Human approval and confidence}
    E -->|Review| F[Audit and review queue]
    E -->|Approved| G[Transactional CRM update]
    G --> H[Idempotency record]
```

The offline run demonstrates four CRM outcomes:

```text
review → applied → duplicate → review
```

The customer is changed once. Replaying the approved event is a no-op;
malformed output is audited for review. [See the saved example report](examples/report.json).

## Integration materials

- [Project case notes: contribution, scope and evidence](docs/project-cases.md)
- [Architecture and failure boundaries](docs/architecture.md)
- [ElevenLabs / creator-operations mapping](docs/elevenlabs.md)
- [Importable n8n validation reference](n8n/crm-review-workflow.json)
- [Synthetic example transcript](examples/transcript.txt)
- [Privacy model and publication checks](docs/privacy.md)

The n8n reference demonstrates validation and review routing; persistence and
idempotency are implemented in the Python demonstration. Live provider adapters,
SIP registration, production identity/access controls and a review UI are outside
this repository's scope. These demos do not measure recognition quality, business
ROI or real-call latency.

## Background

- Over 10 years of management experience, including procurement and logistics;
  P&L responsibility for a distributor with annual turnover exceeding $20M.
- Practical n8n/API, PostgreSQL/Supabase, Codex/Claude Code and VS Code workflows.
- Project experience with Asterisk/SIP/AudioSocket, real-time speech APIs,
  transcription, tool calling and Obsidian/RAG workflows.
- MIET Specialist Diploma, five-year programme in Economics and Marketing;
  postgraduate international study in Marbella, Spain.
- English: fluent business/technical communication. Russian: native.
  Spanish: reading and correspondence; limited conversational proficiency.

**Location:** CIS region. **Contact:** bolesusi147@gmail.com.
