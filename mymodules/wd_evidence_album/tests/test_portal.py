from odoo.tests.common import TransactionCase

from ..controllers.portal import EvidenceAlbumPortal


class TestEvidenceAlbumPortalRanges(TransactionCase):
    def test_range_bounds(self):
        self.assertEqual(EvidenceAlbumPortal._range_bounds("bytes=2-5", 10), (2, 5))
        self.assertEqual(EvidenceAlbumPortal._range_bounds("bytes=7-", 10), (7, 9))
        self.assertEqual(EvidenceAlbumPortal._range_bounds("bytes=-3", 10), (7, 9))
        self.assertIsNone(EvidenceAlbumPortal._range_bounds("bytes=10-12", 10))
        self.assertIsNone(EvidenceAlbumPortal._range_bounds("bytes=0-0,2-3", 10))
