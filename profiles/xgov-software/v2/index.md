# XGov software discovery profile v2

Status: experimental implementation profile, adopted by this producer on
23 November 2026. This is a producer-specific OKF+ profile. It does not claim
conformance to the full Bundle Wiki v2 profile.

The profile applies [OKF core 0.3](https://github.com/open-knowledge-format/open-knowledge-format/blob/527e81aff55992be21507e97004286789126f88c/SPEC.md)
to the typed Markdown taxonomy concepts generated from `config/taxonomy.json`.
The common [repository semantic contract v2](../../../schemas/standard/v2/repository-contract.schema.json)
declares the core version. Frozen v1 schemas and contexts and the existing
custom assertion contract remain unchanged historical dependencies.

## Source and projections

- `config/taxonomy.json` is the authoritative source for 47 typed Markdown
  concepts. Generated Markdown retains JSON-valued YAML frontmatter and an
  evidence-qualified body. The generated core Reader projection carries the
  full body, frontmatter, source path and SHA-256 for each page.
- Semantic identifiers and routes remain stable. Core source paths use
  `concepts/<scheme>/<id>.md`; existing semantic routes use
  `<scheme>/<id>.md`. The projection records both explicitly.
- The large catalogue graph is a separate extension for source-backed
  repository metadata and assertions. Its virtual Reader routes do not create
  authored Markdown. Extension rows are labelled `extension`; taxonomy pages
  alone are core concepts. Navigation is not promoted into the concept graph.
- Core reference pairs are zero in the current taxonomy source. The graph does
  not invent links between concepts.
- The generated `source/taxonomy.json` is an Explorer runtime resource that
  exposes the taxonomy source projection used by the core-only walkthrough. The
  generated `walkthrough/**` files are source-linked validation material, not
  authored core concepts or additional graph edges.
- The 29 October 2026 published input set is pinned to its archived source and
  contributor-history packages. A separate 28 October checked-in input
  baseline remains available for compatibility comparison. Neither is a fresh
  source observation.

## Interpretation limits

Taxonomy classifications are experimental, unreviewed matches against
repository names and descriptions. Repository licence, programming language,
SBOM reference, dates, stars and contributor statistics are source-reported
metadata, not permission to reuse, code review, SBOM inspection, security
assurance, maintainer evidence or an exhaustive inventory. History can include
inherited fork activity and is limited to captured provider responses. Missing
history is not zero activity. The archive includes metadata only and does not
execute catalogued repository code.

The common contract schema validates contract shape. Linking to a shared
profile or passing a Reader journey does not establish specialist acceptance,
classification accuracy, public release or operational approval.
