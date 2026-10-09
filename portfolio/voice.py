"""AudioSocket framing and a fixture-driven voice lifecycle; no live provider."""
import struct


class FrameDecoder:
    """Decode packet type + uint16 big-endian length + payload across TCP chunks."""
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, chunk: bytes) -> list[tuple[int, bytes]]:
        if not isinstance(chunk, bytes) or len(chunk) > 65536:
            raise ValueError('Expected a bounded bytes chunk')
        self.buffer.extend(chunk)
        result = []
        while len(self.buffer) >= 3:
            kind = self.buffer[0]
            length = struct.unpack('>H', self.buffer[1:3])[0]
            if length > 4096:
                raise ValueError('Frame payload exceeds demo limit')
            if len(self.buffer) < length + 3:
                break
            payload = bytes(self.buffer[3:length+3])
            del self.buffer[:length+3]
            if kind == 0x10 and length % 2:
                raise ValueError('PCM16 payload must contain whole samples')
            if kind == 0 and length:
                raise ValueError('Hangup packet must be empty')
            if kind == 1 and length != 16:
                raise ValueError('Call identifier must contain 16 bytes')
            result.append((kind, payload))
        return result

    def finish(self) -> None:
        if self.buffer:
            raise ValueError('Truncated AudioSocket frame')


class VoiceSession:
    """Explicit lifecycle for an offline provider simulator, not speech generation."""
    def __init__(self):
        self.state = 'listening'
        self.provider = 'primary'
        self.queued_audio = b''
        self.trace = []

    def handle(self, event: str, audio: bytes = b'') -> dict:
        if self.state == 'closed':
            raise ValueError('Session is closed')
        if event == 'answer':
            if not isinstance(audio, bytes) or not audio or len(audio) % 2 or len(audio) > 65536:
                raise ValueError('Expected bounded nonempty PCM16 bytes')
            self.queued_audio = audio
            self.state = 'speaking'
        elif event == 'interrupt':
            self.queued_audio = b''
            self.state = 'listening'
        elif event == 'timeout':
            self.queued_audio = b''
            if self.provider == 'primary':
                self.provider = 'fallback'
                self.state = 'listening'
            else:
                self.provider = 'unavailable'
                self.state = 'closed'
        elif event == 'hangup':
            self.queued_audio = b''
            self.state = 'closed'
        else:
            raise ValueError('Unknown lifecycle event')
        result = dict(event=event, state=self.state, provider=self.provider,
                      queued_samples=len(self.queued_audio)//2)
        self.trace.append(result)
        return result


def catalog_lookup(arguments: dict) -> dict:
    """Allowlisted read-only tool. Catalogue content and stock are fictional."""
    if not isinstance(arguments, dict) or set(arguments) != {'part'}:
        raise ValueError('Only the part argument is supported')
    part = arguments['part']
    if not isinstance(part, str) or not part.strip() or len(part) > 64:
        raise ValueError('Invalid part name')
    if part.strip().upper() == 'DEMO-ADC':
        return dict(found=True, part='DEMO-ADC', description='Fictional ADC for the demo',
                    stock=12, synthetic=True)
    return dict(found=False, synthetic=True)
