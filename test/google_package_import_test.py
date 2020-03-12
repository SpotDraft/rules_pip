import unittest


class TestGooglePackageImportTest(unittest.TestCase):
    def test_import_pubsub_first(self):
        from google.cloud import pubsub
        from google.cloud import vision

    def test_import_vision_first(self):
        from google.cloud import vision
        from google.cloud import pubsub

    def test_import_vision_first_2(self):
        import google.auth
        from google.cloud import vision
        from google.cloud import pubsub


if __name__ == "__main__":
    unittest.main()