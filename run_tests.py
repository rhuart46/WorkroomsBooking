"""
Launch the API from the root of the project.
"""
import os
import sys
import unittest


def launch() -> None:
    # Set the src/ directory as the root of the source code:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, "src")
    sys.path.insert(0, src_dir)

    os.environ["ENVIRONMENT"] = "test"

    # Gather and launch the tests:
    suit = unittest.TestSuite()
    itests_dir = os.path.join(current_dir, "itests")
    suit.addTest(unittest.defaultTestLoader.discover(itests_dir, pattern="itest_*.py"))
    runner = unittest.TextTestRunner()
    runner.run(suit)


if __name__ == "__main__":
    launch()
