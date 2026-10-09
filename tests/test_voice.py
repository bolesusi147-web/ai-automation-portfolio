import struct
import unittest

from portfolio.voice import FrameDecoder, VoiceSession, catalog_lookup


class VoiceTests(unittest.TestCase):
    def test_fragmented_frames_preserve_pcm(self):
        decoder = FrameDecoder()
        frame = b'\x10\x00\x04\x01\x00\x02\x00'
        self.assertEqual(decoder.feed(frame[:2]), [])
        self.assertEqual(decoder.feed(frame[2:5]), [])
        self.assertEqual(decoder.feed(frame[5:]), [(0x10, b'\x01\x00\x02\x00')])
        decoder.finish()

    def test_multiple_frames_and_hangup(self):
        self.assertEqual(FrameDecoder().feed(b'\x10\x00\x02\x01\x00\x00\x00\x00'),
                         [(0x10, b'\x01\x00'), (0, b'')])

    def test_truncated_frame_is_rejected(self):
        decoder = FrameDecoder()
        decoder.feed(b'\x10\x00\x04\x01')
        with self.assertRaises(ValueError): decoder.finish()

    def test_oversized_and_odd_pcm_are_rejected(self):
        for frame in [b'\x10'+struct.pack('>H',4097), b'\x10\x00\x01\x01']:
            with self.subTest(frame=frame[:3]):
                with self.assertRaises(ValueError): FrameDecoder().feed(frame)

    def test_interruption_discards_stale_playback(self):
        session=VoiceSession(); session.handle('answer', b'\x01\x00'*3)
        self.assertEqual(session.state,'speaking')
        session.handle('interrupt')
        self.assertEqual((session.state,session.queued_audio),('listening',b''))

    def test_provider_failure_is_bounded_and_clears_audio(self):
        session=VoiceSession(); session.handle('answer',b'\x01\x00')
        session.handle('timeout')
        self.assertEqual((session.provider,session.queued_audio),('fallback',b''))
        session.handle('timeout')
        self.assertEqual((session.provider,session.state),('unavailable','closed'))
        with self.assertRaises(ValueError): session.handle('answer',b'\x01\x00')

    def test_catalogue_tool_has_no_arbitrary_execution(self):
        self.assertEqual(catalog_lookup({'part':'DEMO-ADC'})['stock'],12)
        self.assertEqual(catalog_lookup({'part':'MISSING'})['found'],False)
        for args in [{'part':'DEMO-ADC','command':'anything'}, {'part':['DEMO-ADC']}, {'part':'x'*100}]:
            with self.assertRaises(ValueError): catalog_lookup(args)
