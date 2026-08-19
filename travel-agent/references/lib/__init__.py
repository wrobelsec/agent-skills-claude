"""Shared helpers for the travel-agent scripts.

Split deliberately: `lib/` is imported, `scripts/` is run. Anything used by more
than one script belongs here, because the alternative is copies that drift --
the currency symbol map once existed in two files and printed two different
things for the same price.
"""
