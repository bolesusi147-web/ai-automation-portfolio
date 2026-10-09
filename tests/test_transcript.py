import struct
import unittest
from portfolio.transcript import split_stereo, build_dialogue


class TranscriptTests(unittest.TestCase):
    def test_stereo_samples_are_separated_without_swapping(self):
        left,right=split_stereo(struct.pack('<hhhh',100,200,-100,-200))
        self.assertEqual(struct.unpack('<hh',left),(100,-100))
        self.assertEqual(struct.unpack('<hh',right),(200,-200))

    def test_partial_stereo_sample_is_rejected(self):
        with self.assertRaises(ValueError): split_stereo(b'\x00'*3)

    def test_chronology_roles_and_overlapping_merge(self):
        words=[{'channel':1,'start':2,'end':3,'text':'Please send a quote.','energy':50},
               {'channel':0,'start':0,'end':2,'text':'Hello.','energy':100},
               {'channel':0,'start':1,'end':1.5,'text':'How can I help?','energy':100}]
        turns=build_dialogue(words,manager_channel=0)
        self.assertEqual([(t['role'],t['start'],t['end']) for t in turns],
                         [('manager',0,2),('customer',2,3)])
        self.assertEqual(turns[0]['text'],'Hello. How can I help?')

    def test_cross_channel_echo_suppression_uses_time_and_energy(self):
        words=[{'channel':0,'start':0,'end':1,'text':'Hello!','energy':100},
               {'channel':1,'start':0.1,'end':1,'text':'hello','energy':5},
               {'channel':1,'start':3,'end':4,'text':'hello','energy':50}]
        turns=build_dialogue(words,manager_channel=0)
        self.assertEqual(len(turns),2)
        self.assertEqual(turns[1]['start'],3)

    def test_invalid_time_channel_and_nonfinite_values_are_rejected(self):
        base={'channel':0,'start':0,'end':1,'text':'Hello','energy':10}
        for change in [{'end':-1},{'start':float('nan')},{'channel':2},{'channel':True},{'text':''},{'energy':float('inf')},{'start':10**400}]:
            with self.subTest(change=change):
                with self.assertRaises(ValueError): build_dialogue([base|change],manager_channel=0)
        with self.assertRaises(ValueError): build_dialogue([base],manager_channel=True)
