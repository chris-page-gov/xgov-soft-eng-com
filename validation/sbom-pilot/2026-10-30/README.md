# Public SBOM pilot implementation checks

These are implementation checks observed on 30 October 2026, not results from
a real SBOM pilot. No catalogue SBOM was fetched or matched, no candidate
finding was published and no model or maintainer communication was invoked.
The [machine-readable receipt](implementation-verification.json) binds the
runner, pins, example and synthetic test source by SHA-256.

- All 122 unit/regression tests passed, including 52 synthetic pilot cases.
- The example dry-run admitted one entry for later retrieval, with zero
  requests, zero scanner invocations and no claimed owner approval.
- Official scanner/download checksums and database bytes were verified. Grype
  0.121.0 version metadata and database import ran with network access denied.
  Two imports produced the same prepared SQLite hash. No SBOM was supplied.
- The existing local frozen source passed build, deterministic lockstep and
  independent assurance: 24,068 records, 113,825 assertions and 3,159,441 RDF
  triples, with two repository contracts validated and no remote contexts.
- The local archive's ten offline checks and Pages staging passed with the
  private tool cache present. Neither includes private pilot or consent paths.
- Refresh, history and Pages workflow bytes are unchanged; their hashes are
  retained in the receipt. No schedule, repository variable or deployment was
  changed by this implementation.

The local frozen-source checks are separate from the current published
catalogue. No new dataset snapshot or Pages deployment is claimed. The public
pin/implementation evidence contains no repository-specific advisory matches.
Actual inputs, caches, checkpoints, JSON/Markdown candidate reports and raw
scanner output belong only under the ignored private `.sbom-pilot/` root.

The [runner guide](../../../docs/public-sbom-pilot.md) records commands, bounds,
admission and limitations. Matching supports the documented JSON formats and
eight language PURL ecosystems. macOS ARM64 preparation was exercised; the
Linux namespace path is mocked. Real matching compatibility, performance,
applicability and deployment exposure remain untested.
