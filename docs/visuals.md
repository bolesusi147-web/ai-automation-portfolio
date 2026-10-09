# Portfolio visuals

The README uses three reviewed graphics:

- [Cover](../assets/portfolio-cover.png): an AI-generated editorial illustration
  of voice, structured information, human review and business integrations.
  The illustrated person is a generic reviewer, not a portrait.
- [Animated workflow](../assets/workflow.gif): a 13.44-second illustrated story
  with synthetic inputs and five stages: request, structured output, human
  review, an applied update and a skipped duplicate.
- [Static workflow](../assets/workflow.png): the same process with its final
  duplicate-safe outcome, available for readers who prefer a still image.

The graphics are conceptual illustrations, not product screenshots or live
provider output. The CRM state and action labels come from the existing fixture;
review, applied and duplicate outcomes are present in the runnable example.
The animation does not imply a working human-review UI or a single deployed
system joining all three demonstrations.

## Rebuilding the workflow graphics

Only asset authoring needs Pillow and the DejaVu Sans fonts. The default demos,
publication scanner and unit tests continue to use the Python standard library.

```bash
python3 -m pip install Pillow
python3 tools/render_workflow.py
```

Review the resulting PNG and every storyboard stage before changing their
fingerprints in [the visual manifest](../assets/manifest.json). The scanner
permits only the three named README assets with reviewed SHA256 fingerprints,
bounded file size and matching PNG/GIF format. Changed or unapproved binaries
fail publication checks. Historical fingerprints are read from committed
manifests so older reviewed versions can still be checked.

Fingerprint and file-format checks do not inspect image pixels. Visual review
is required to catch real customer details or other inappropriate imagery.
Do not register real recordings, screenshots of private systems or credentials.
