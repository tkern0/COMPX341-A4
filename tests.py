import re
import unittest
import urllib2
import urlparse

RE_PASS = re.compile(r"(\d+) is prime")
RE_FAIL = re.compile(r"(\d+) is not prime")

def load_page(page):
  url = urlparse.urljoin("http://localhost:42731", page)
  try:
    req = urllib2.urlopen(url)
    return {"code": req.getcode(), "content": req.read()}
  except urllib2.HTTPError, e:
    return {"code": e.code, "content": None}

class TestURL(unittest.TestCase):
  def test_text_prime(self):
    self.assertEquals(load_page("isPrime/seven")["code"], 404)

  def test_no_prime(self):
    self.assertEquals(load_page("isPrime")["code"], 404)

  def test_basic_primes(self):
    self.assertRegexpMatches(load_page("isPrime/0")["content"], RE_FAIL)
    self.assertRegexpMatches(load_page("isPrime/1")["content"], RE_FAIL)
    self.assertRegexpMatches(load_page("isPrime/2")["content"], RE_PASS)
    self.assertRegexpMatches(load_page("isPrime/3")["content"], RE_PASS)
    self.assertRegexpMatches(load_page("isPrime/4")["content"], RE_FAIL)

  def test_advanced_primes(self):
    primes = [
      7727, 7741, 7753, 7757, 7759, 7789, 7793, 7817, 7823, 7829, 7841, 7853,
      7867, 7873, 7877, 7879, 7883, 7901, 7907, 7919
    ]
    for i in range(min(primes), max(primes) + 1):
      req = load_page("isPrime/" + str(i))
      self.assertEquals(req["code"], 200)
      match = (RE_PASS if i in primes else RE_FAIL).match(req["content"])
      self.assertIsNotNone(match)
      self.assertEquals(int(match.group(1)), i)

  def test_stored_primes(self):
    # Store all reported primes in the first 250
    found_primes = set()
    for i in range(250):
      req = load_page("isPrime/" + str(i))
      self.assertEquals(req["code"], 200)
      if RE_PASS.match(req["content"]) != None:
        found_primes.add(i)
    # Load the list of stored primes (as a set of ints)
    req = load_page("primesStored")
    self.assertEquals(req["code"], 200)
    strNums = req["content"].split(", ")
    stored = set()
    for val in strNums:
      stored.add(int(val))
    # Make sure all our found primes are part of the stored ones
    self.assertTrue(found_primes.issubset(stored))

unittest.main()
