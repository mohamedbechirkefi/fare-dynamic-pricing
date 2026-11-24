<!-- SPDX-License-Identifier: LicenseRef-FARE-NC-Research-1.0 -->
# tests/

The suite covers:

- unit tests for the parameters, streams, policies, metrics, statistics and tuning, including invalid inputs;
- Hypothesis property tests: stock conservation, price bounds and exact policy nesting (k = 0 and eta = 0 reproduce FIX);
- a differential test of the fast simulator against a naive buyer-by-buyer oracle;
- hand-computed golden examples for FIX, OCC and DRP;
- no-demand, sold-out, zero-capacity and extreme-parameter cases;
- config-to-results integration tests, schema rejection of malformed results, the freeze guard and report generation.

Run it with `PYTHONPATH=src uv run --frozen python -m fare.cli test`.
