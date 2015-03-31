import unittest

from networking.base import get_local_addr

class NetworkingTests(unittest.TestCase):
    def test_get_ip_addr(self):
        self.assertEqual(get_local_addr(), '192.168.0.106')  # Hard coding as it is
