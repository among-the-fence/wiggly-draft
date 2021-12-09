import unittest

from app import collage


class MyTestCase(unittest.TestCase):
    def test_collage(self):
        collage(["imagecache/abaddon_lg.png","imagecache/abaddon_lg.png","imagecache/abaddon_lg.png","imagecache/abaddon_lg.png","imagecache/abaddon_lg.png","imagecache/abaddon_lg.png"])


if __name__ == '__main__':
    unittest.main()
