"""Test suite for the travel-agent skill.

Two tiers, deliberately separated:

  * UNIT tests run offline against fabricated fixtures. They are fast, need no
    key and no network, and they guard the transformations that have actually
    broken in production -- currency formatting, machine-value translation,
    link injection, heading ownership.

  * LIVE tests hit the network. They answer a different question: are the
    endpoints this skill depends on reachable *today*, and does a keyed
    provider give the right answer *for this destination*.

Run both from scripts/run_tests.py. Nothing here imports a destination: unit
fixtures are invented, and the live destination probe takes its address and
bounding box as arguments, because a probe only works against an answer you
already know.
"""
