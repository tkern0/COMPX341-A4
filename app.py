import time

import redis
from flask import Flask

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

def redis_command(function):
  retries = 5
  while True:
    try:
      return function()
    except redis.exceptions.ConnectionError as exc:
      if retries == 0:
        raise exc
      retries -= 1
      time.sleep(0.5)

def get_hit_count():
  return redis_command(lambda: cache.incr('hits'))

@app.route('/')
def hello():
  count = get_hit_count()
  return 'Hello World! I have been seen {} times.\n'.format(count)

def get_all_primes():
  return redis_command(_all_primes_converter)
def _all_primes_converter():
  all_primes = cache.smembers("primes")
  if all_primes == None:
    return set()
  output = set()
  for i in all_primes:
    output.add(int(i.decode("ascii")))
  return output

def in_primes(number):
  return redis_command(lambda: cache.sismember("primes", number))

def add_prime(number):
  redis_command(lambda: cache.sadd("primes", number))


@app.route("/isPrime/<int:number>")
def is_prime(number):
  prime = True
  if not in_primes(number):
    if number <= 1:
      prime = False
    else:
      for i in range(2, int(number**0.5) + 1):
        if number % i == 0:
          prime = False
          break
    if prime:
      add_prime(number)
  if prime:
    return str(number) + " is prime"
  else:
    return str(number) + " is not prime"

@app.route("/primesStored")
def primes_stored():
  output = ""
  all_primes = sorted(list(get_all_primes()))
  for i in all_primes:
    output += str(i) + ", "
  return output[:-2]
