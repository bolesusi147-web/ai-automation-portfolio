# Project experience behind the demonstrations

These case notes describe my project experience; the public runnable examples are
independent reconstructions using fictional inputs. They are not exports of the
private systems. No production accuracy or ROI measurements are claimed here.

## Business workflows and CRM/ERP integration

**Problem:** Manager messages, emails, calls, product availability and orders
needed to become usable business records rather than disconnected information.

**My contribution:** Led AI-assisted implementation of n8n/API workflows,
structured CRM updates and summaries, and integration with an ERP-connected B2B
portal for prices, availability, orders and invoices. Worked on BOM parsing, MPN
matching and supplier-offer comparison, with datasheet links for component search.

**Relevant tools:** n8n, REST APIs, PostgreSQL, Supabase/PostgREST, SQL,
JavaScript/TypeScript and AI coding tools in VS Code.

**What the demo shows:** Strict structured-output boundaries, trusted customer
routing, approval, duplicate delivery handling, and a transaction/audit record.
This is the portion a recruiter can run without access to the business systems.

## Call transcription and conversation analysis

**Problem:** Stereo call recordings needed channel-aware transcripts, speaker
roles, timestamps, summaries and links to the correct CRM record.

**My contribution:** Led AI-assisted implementation and troubleshooting of
channel separation, speech gating, transcription and dialogue reconstruction.
Prepared a corpus of **818 manager-call dialogues** and investigated cross-channel
leakage, speaker-role errors and persistence issues. This count describes data
volume, not recognition accuracy or a measured revenue increase.

**What the demo shows:** PCM separation, chronological reconstruction, explicit
role mapping and an illustrative overlapping-echo heuristic. Actual STT responses
are replaced with fixtures; no real call recording is distributed.

## Conversational voice agent for business telephony

**Problem:** Connect a voice assistant to SIP telephony and business tools while
handling audio timing, interruptions, provider errors and tool results.

**My contribution:** Led AI-assisted development and troubleshooting around
Asterisk/AudioSocket, Python, real-time speech APIs, product/specification tool
calling, logs and provider fallback. Project experience included OpenAI, Gemini
Live and Yandex speech APIs; this is not a statement about the current production
provider or an ElevenLabs integration.

**What the demo shows:** Fragmented AudioSocket packets, bounded PCM, interruption
and fallback state, and an allowlisted read-only catalogue tool. The demo does not
reproduce a deployed SIP service or measure real-call latency.

## Additional experimental work

I have also worked on Obsidian/RAG knowledge workflows and image/video pipelines
with ComfyUI, Runpod, SDXL/LoRA, FLUX, Wan, LTX and Higgsfield. These are
experimental projects. No client media, personal-image datasets or private GPU
configuration is included in this repository.
