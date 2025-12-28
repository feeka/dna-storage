#!/usr/bin/env python3
"""Run test functions directly for environments without pytest."""
import importlib.util
import sys
import os

p = os.path.join(os.path.dirname(__file__), '..')
# ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(p))

spec = importlib.util.spec_from_file_location("test_gen", os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_gen_synthetic_reads.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

print('Running test_mutate_seq_basic...')
mod.test_mutate_seq_basic()
print('test_mutate_seq_basic: OK')

print('Running test_generator_creates_ndjson_and_is_deterministic...')
mod.test_generator_creates_ndjson_and_is_deterministic()
print('test_generator_creates_ndjson_and_is_deterministic: OK')

print('All manual tests passed')
