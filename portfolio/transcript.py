"""Stereo PCM preprocessing and validated fixture transcripts; no real STT."""
import math
import re
import struct


def split_stereo(pcm: bytes) -> tuple[bytes, bytes]:
    if not isinstance(pcm, bytes) or len(pcm) % 4:
        raise ValueError('Expected complete interleaved stereo PCM16 frames')
    left, right = bytearray(), bytearray()
    for offset in range(0, len(pcm), 4):
        left.extend(pcm[offset:offset+2])
        right.extend(pcm[offset+2:offset+4])
    return bytes(left), bytes(right)


def rms(pcm: bytes) -> float:
    if len(pcm) % 2:
        raise ValueError('Partial PCM16 sample')
    if not pcm:
        return 0.0
    samples = struct.unpack('<'+'h'*(len(pcm)//2), pcm)
    return math.sqrt(sum(v*v for v in samples)/len(samples))


def _number(value) -> bool:
    if not isinstance(value,(int,float)) or isinstance(value,bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def build_dialogue(segments: list[dict], manager_channel: int) -> list[dict]:
    """Remove matching weaker overlapping echoes; merge neighbouring same-role turns.

    Manager channel is explicit metadata, not an inferred identity. Echo suppression
    is a heuristic and requires real-world calibration outside this demonstration.
    """
    if type(manager_channel) is not int or manager_channel not in (0,1):
        raise ValueError('Manager channel must be 0 or 1')
    if not isinstance(segments,list) or len(segments) > 1000:
        raise ValueError('Expected a bounded segment list')
    clean = []
    for segment in segments:
        if not isinstance(segment,dict):
            raise ValueError('Invalid segment')
        channel,start,end,text,energy = (segment.get(k) for k in ('channel','start','end','text','energy'))
        if type(channel) is not int or channel not in (0,1):
            raise ValueError('Invalid channel')
        if not _number(start) or not _number(end) or start < 0 or end <= start:
            raise ValueError('Invalid timestamps')
        if not isinstance(text,str) or not text.strip() or len(text)>4000:
            raise ValueError('Invalid segment text')
        if not _number(energy) or energy < 0:
            raise ValueError('Invalid signal energy')
        clean.append(dict(channel=channel,start=start,end=end,text=text.strip(),energy=energy))
    keep = [True]*len(clean)
    normalize = lambda text: re.sub(r'[^\w\s]','',text.casefold()).strip()
    for i,a in enumerate(clean):
        for j in range(i+1,len(clean)):
            b = clean[j]
            if not keep[i] or not keep[j] or a['channel']==b['channel']:
                continue
            overlap = min(a['end'],b['end'])-max(a['start'],b['start'])
            if overlap <= 0.5*min(a['end']-a['start'],b['end']-b['start']):
                continue
            if normalize(a['text']) == normalize(b['text']):
                keep[j if a['energy']>=b['energy'] else i] = False
    turns = [dict(role='manager' if s['channel']==manager_channel else 'customer',
                  start=s['start'],end=s['end'],text=s['text']) for s,k in zip(clean,keep) if k]
    turns.sort(key=lambda t:(t['start'],t['role']))
    merged = []
    for turn in turns:
        if merged and merged[-1]['role']==turn['role'] and turn['start']-merged[-1]['end']<0.8:
            merged[-1]['text'] += ' '+turn['text']
            merged[-1]['end'] = max(merged[-1]['end'],turn['end'])
        else:
            merged.append(dict(turn))
    return merged
