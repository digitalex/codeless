# Codeless AI -- Write systems, not code
Codeless is to to Python code what a compiler is to machine code. You write the interface, you approve the tests, the AI writes the implementation. You should not have to ever look at the implementation, just like you should never have to inspect the machine code produced by a compiler. If the tests pass, why ever look at the code? Uncertain that the code is correct? Write more tests!

## Getting started

Set up environment:

```bash
git clone https://github.com/digitalex/codeless.git
cd codeless
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt
```

Add API keys to `.env`, e.g.:

```
OPENAI_API_KEY=<secret>
GEMINI_API_KEY=<secret>
ANTHROPIC_API_KEY=<secret>
```

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

Codeless will now iterate on an implementation that passes the tests. It'll tell you when it's done.

### What's next?

You can add to the interface, or the tests, or both. Watch the terminal window to allow codeless to improve the implementation.

Tip: Try prompting your favorite IDE to design the subsystem for you. Tell it to make an abstract python class.
