# Architecture and failure boundaries

## Voice transport and lifecycle

| Current state | Event | Next state | Handling |
|---|---|---|---|
| Start | Session initialised | Listening | Wait for input |
| Listening | Answer queued | Speaking | Play the queued response |
| Speaking | Interrupt | Listening | Clear queued PCM |
| Listening | Primary timeout | Listening | Switch to the fallback provider |
| Speaking | Primary timeout | Listening | Clear queued PCM and switch to fallback |
| Listening | Fallback timeout or hangup | Closed | End the session |
| Speaking | Hangup | Closed | End the session |

`FrameDecoder` accepts packet type, two-byte big-endian length and payload across
arbitrary bounded byte chunks. PCM16 must contain whole samples; incomplete frames
are rejected on finish. UUID and hangup lengths are checked. Other packet types
remain opaque: this decoder is not a complete Asterisk server.

`VoiceSession` models playback/interruption/fallback state. Its providers are
simulated; it makes no WebSocket connection. A production adapter would translate
provider audio, interruption and tool events into these operations, with timeouts,
bounded queues and cancellation. An AudioSocket unit test is not a test of the
complete SIP/provider/audio path.

## Transcript reconstruction

`split_stereo` separates interleaved little-endian PCM16 samples without changing
channels. Fixture STT segments carry channel, start/end time, text and energy.
The demo validates these values, removes exact normalised text when sufficiently
overlapping on another weaker channel, and merges neighbouring same-role segments.
This is an illustrative echo heuristic: identical overlapping speech can be real,
so thresholds and role metadata need real-world evaluation. Speaker mapping is
supplied explicitly rather than represented as proven diarisation.

## Transactional CRM processing

The model may propose four fields: status, summary, confidence and next_action.
Customer routing and human approval are caller-controlled, separate metadata.
Unsupported fields/actions and invalid JSON cannot update the customer.
Schema checks do not establish factual accuracy: summaries need human review.

SQLite's immediate transaction surrounds duplicate detection, customer mutation
and audit insertion. An identical retry returns `duplicate`; a reused event ID
with a different payload, customer or approval value is rejected. Approved review
results must use a new event ID. A real deployment also needs authenticated
approval, durable review storage, migrations, backpressure and authorised access.

The offline demo sends no email, charges no account and calls no provider API.
