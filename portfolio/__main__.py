"""Run all synthetic demonstrations with: python -m portfolio demo."""
import argparse
import json
import math
from pathlib import Path
import struct
import wave

from .operations import EventStore
from .transcript import split_stereo, build_dialogue, rms
from .voice import FrameDecoder, VoiceSession, catalog_lookup


FIXTURES = Path(__file__).resolve().parent.parent/'fixtures'


def run_demo(output: Path) -> dict:
    # Deliberately refuse existing output: never erase a previous demonstration.
    output.mkdir(parents=True, exist_ok=False)
    stereo = bytearray()
    for index in range(1600):
        left = int(1000*math.sin(2*math.pi*440*index/8000)) if index<800 else 0
        right = int(1000*math.sin(2*math.pi*660*index/8000)) if index>=800 else 0
        stereo.extend(struct.pack('<hh',left,right))
    with wave.open(str(output/'stereo-test.wav'),'wb') as wav:
        wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(8000)
        wav.writeframes(stereo)
    left,right = split_stereo(bytes(stereo))
    call = json.loads((FIXTURES/'call_segments.json').read_text())
    turns = build_dialogue(call['segments'],call['manager_channel'])
    text = '\n'.join(f"[{t['start']:05.2f}–{t['end']:05.2f}] {t['role'].upper()}: {t['text']}" for t in turns)
    (output/'transcript.txt').write_text('SYNTHETIC TRANSCRIPT — fixture STT, not recognised speech\n'+text+'\n')
    (output/'dialogue.json').write_text(json.dumps(turns,indent=2)+'\n')

    pcm = left[:160]
    packets = b'\x10'+struct.pack('>H',len(pcm))+pcm+b'\x00\x00\x00'
    decoder = FrameDecoder()
    frames = []
    for offset in range(0,len(packets),17):
        frames.extend(decoder.feed(packets[offset:offset+17]))
    decoder.finish()
    session = VoiceSession()
    session.handle('answer',pcm)
    session.handle('interrupt')
    session.handle('timeout')
    tool_result = catalog_lookup({'part':'DEMO-ADC'})
    session.handle('answer',pcm)
    session.handle('hangup')
    (output/'voice-trace.json').write_text(json.dumps(session.trace,indent=2)+'\n')

    model = json.loads((FIXTURES/'model_response.json').read_text())['analysis']
    with EventStore(output/'audit.db') as store:
        results = [store.ingest('evt-review','DEMO-CUSTOMER',model),
                   store.ingest('evt-approved','DEMO-CUSTOMER',model,approved=True),
                   store.ingest('evt-approved','DEMO-CUSTOMER',model,approved=True),
                   store.ingest('evt-malformed','DEMO-CUSTOMER','malformed JSON',approved=True)]
        crm = dict(outcomes=[r['outcome'] for r in results],audit_events=store.event_count(),
                   final_customer=store.customer('DEMO-CUSTOMER'))
    (output/'crm-events.json').write_text(json.dumps(results,indent=2)+'\n')
    report = dict(synthetic=True,network_calls=0,providers='fixture STT/LLM; synthetic PCM tones',
                  voice=dict(transport_frames=len(frames),final_state=session.state,
                             tool_result=tool_result,events=session.trace),
                  transcript=dict(turn_count=len(turns),input_segments=len(call['segments']),
                                  left_rms=round(rms(left),2),right_rms=round(rms(right),2)),
                  crm=crm)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['demo'])
    parser.add_argument('--output',type=Path,default=Path('.demo-output'))
    args=parser.parse_args()
    try:
        report=run_demo(args.output)
    except FileExistsError:
        parser.error('Output directory already exists; choose a new --output path.')
    print(json.dumps(dict(output=str(args.output),synthetic=report['synthetic'],
                          network_calls=0,crm_outcomes=report['crm']['outcomes']),indent=2))


if __name__=='__main__':
    main()
