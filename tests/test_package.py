import unittest

from transkribus_utils import ACDHTranskribusUtils

CLIENT = ACDHTranskribusUtils()
COL_NAME = "bv-play"
COL_ID = 188933


class TestTestTest(unittest.TestCase):
    """Tests for `acdh_cidoc_pyutils` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_001_smoke(self):
        self.assertEqual(1, 1)

    def test_002_init(self):
        client = CLIENT
        self.assertTrue("http" in client.base_url)

    def test_003_get_or_create_col(self):
        client = CLIENT
        col = client.get_or_create_collection(COL_NAME)
        self.assertEqual(col, COL_ID)
