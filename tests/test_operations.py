import tempfile
import unittest
from pathlib import Path
from portfolio.operations import EventStore, validate_analysis


GOOD={'status':'quote_requested','summary':'Customer requested a quotation.','confidence':0.9,'next_action':'follow_up'}


class OperationsTests(unittest.TestCase):
    def test_schema_does_not_coerce_bools_or_route_from_model(self):
        for change in [{'confidence':True},{'confidence':float('nan')},{'confidence':1.1},
                       {'customer_id':'other'},{'status':'arbitrary'},{'next_action':'send_money'},{'summary':''}]:
            with self.subTest(change=change):
                with self.assertRaises(ValueError): validate_analysis(GOOD|change)

    def test_sqlite_idempotency_survives_connection_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'events.db'
            with EventStore(path) as store:
                result=store.ingest('evt-1','DEMO-CUSTOMER',GOOD,approved=True)
                self.assertEqual(result['outcome'],'applied')
                self.assertEqual(store.customer('DEMO-CUSTOMER')['status'],'quote_requested')
            with EventStore(path) as store:
                self.assertEqual(store.ingest('evt-1','DEMO-CUSTOMER',GOOD,approved=True)['outcome'],'duplicate')
                self.assertEqual(store.event_count(),1)

    def test_unapproved_or_uncertain_output_cannot_mutate_customer(self):
        with EventStore(':memory:') as store:
            self.assertEqual(store.ingest('evt-1','DEMO-CUSTOMER',GOOD)['outcome'],'review')
            self.assertEqual(store.ingest('evt-2','DEMO-CUSTOMER',GOOD|{'confidence':0.4},approved=True)['outcome'],'review')
            self.assertEqual(store.customer('DEMO-CUSTOMER')['status'],'new')
            self.assertEqual(store.event_count(),2)

    def test_malformed_output_is_audited_without_business_mutation(self):
        with EventStore(':memory:') as store:
            self.assertEqual(store.ingest('evt-1','DEMO-CUSTOMER','not JSON',approved=True)['outcome'],'review')
            self.assertEqual(store.customer('DEMO-CUSTOMER')['status'],'new')
            self.assertEqual(store.event_count(),1)

    def test_huge_json_integer_confidence_is_audited_for_review(self):
        with EventStore(':memory:') as store:
            result=store.ingest('evt-large','DEMO-CUSTOMER',GOOD|{'confidence':10**400},approved=True)
            self.assertEqual(result['outcome'],'review')
            self.assertEqual(store.event_count(),1)
            self.assertEqual(store.customer('DEMO-CUSTOMER')['status'],'new')

    def test_conflicting_id_is_not_silently_accepted(self):
        with EventStore(':memory:') as store:
            store.ingest('evt-1','DEMO-CUSTOMER',GOOD,approved=True)
            with self.assertRaises(ValueError): store.ingest('evt-1','DEMO-CUSTOMER',GOOD|{'summary':'Different'},approved=True)
            self.assertEqual(store.customer('DEMO-CUSTOMER')['summary'],GOOD['summary'])
            self.assertEqual(store.event_count(),1)

    def test_unknown_customer_and_invalid_ids_do_not_create_events(self):
        with EventStore(':memory:') as store:
            with self.assertRaises(ValueError): store.ingest('evt-1','other',GOOD,approved=True)
            with self.assertRaises(ValueError): store.ingest('', 'DEMO-CUSTOMER',GOOD)
            self.assertEqual(store.event_count(),0)
