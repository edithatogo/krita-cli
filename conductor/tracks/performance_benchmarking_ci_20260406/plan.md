# Implementation Plan: Performance Benchmarking CI

## Phase 1: Benchmark CI Job
- [ ] Task: Add benchmark job to CI workflow
    - [ ] Implement Feature: Add `benchmark` job to `.github/workflows/ci.yml` that runs `benchmarks/test_rendering.py`
- [ ] Task: Add performance regression detection
    - [ ] Write Tests: Test benchmark comparison logic
    - [ ] Implement Feature: Compare results against baseline; exit with error if >10% regression

## Phase 2: Baseline & History
- [ ] Task: Create baseline management system
    - [ ] Write Tests: Unit tests for baseline loading, saving, comparison
    - [ ] Implement Feature: Store baseline in `benchmarks/baseline.json`; script to update baseline
- [ ] Task: Add benchmark history tracking
    - [ ] Implement Feature: Store results as GitHub artifacts; optional upload to external dashboard

## Phase 3: Memory Profiling
- [ ] Task: Integrate scalene memory profiling
    - [ ] Implement Feature: Add scalene profiling step to CI benchmark job
    - [ ] Implement Feature: Parse scalene output and include memory metrics in benchmark report
