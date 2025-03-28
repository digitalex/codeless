# Codeless AI -- Write systems, not code
Codeless is to to Python code what a compiler is to machine code. You write the interface and review the tests, the AI writes the implementation.

You should never have to look at the implementation any more than you have to inspect the machine code produced by a compiler. If the tests pass, why ever look at the code? Uncertain that the code is correct? Write more tests!

## Getting started

Set up environment:

```bash
git clone https://github.com/digitalex/codeless.git
cd codeless
python3 -m venv .
source bin/activate
python3 -m pip install -r requirements.txt
```

Add API keys to `.env`, e.g.:

```
OPENAI_API_KEY=<secret>
GEMINI_API_KEY=<secret>
ANTHROPIC_API_KEY=<secret>
```

Note that the code by default uses OpenAI (o4) - you can change it in start.py.

If you'd like to set up Logfire, do the following:

## Logfire Setup (optional)

1. Follow [the official documentation](https://logfire.pydantic.dev/docs/how-to-guides/create-write-tokens/) on how to create a logfire token.
2. Add it to `.env`:

```
LOGFIRE_TOKEN=<my new token>
```


## Quick demo

1. Run `python demo.py`.
2. Say 'wow!'
3. Try some more, e.g. `python demo.py microblog`, or `python demo.py snake`.
4. Tell all your friends.


## Using with IDE

In your favorite IDE, open a terminal window and start the listener:

```bash
python start.py my-first-project
```

This will listen to new interface files in ./output/my-first-project/.

Next, create an interface file, for instance `output/my-first-project/math_utils.py`.

```python
from abc import ABC, abstractmethod

class MathUtils(ABC):
    @abstractmethod
    def fibonacci(self, n: int) -> int:
	"""An optimal implementation that returns the Nth fibonacci number."""
	pass

    @abstractmethod
    def gcd(self, nums: list[int]) -> int:
	"""Returns the largest positive integer that can divide all the input numbers without a remainder."""
	pass
```

The listener will ask you to hit enter once you're ready to continue. Do it!

Codeless will now create a test file. Open it in your IDE (for the example, it'll be `output/my-first-project/math_utils_test.py`).

Look at the test. If you're happy with it, let Codeless continue again by hitting enter.

Codeless will now iterate on an implementation that passes the tests. It'll tell you when it's done. This is the magic moment!

## Running tests

```
pytest --ignore=agents/test_generator.py --ignore=lib
```

### What's next?

You can add to the interface, or the tests, or both. Watch the terminal window to allow codeless to improve the implementation.

Tip: Try prompting your favorite AI to design the subsystem for you. Tell it to make an abstract python class.
