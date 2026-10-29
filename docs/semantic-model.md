# Semantic model

The pack uses OKF 0.2 Markdown for its index and concept pages. This document
defines its custom additive semantic profile. It does not claim canonical
Bundle Wiki YAML-LD profile conformance.

All distinct repositories, observed accounts, languages and reported licence
identifiers are represented. Subject/task coverage is bounded by authored
rules and available names/descriptions; unknowns generate no invented edges.
There is no OWL reasoning or claim to understand all domains in repository code.

| Concept | Mapping |
| --- | --- |
| Catalogue and frozen metadata | [DCAT 3](https://www.w3.org/TR/vocab-dcat-3/) `Catalog` and `Dataset` |
| Repository | Custom Repository, with [Schema.org](https://schema.org/SoftwareSourceCode) name, description, codeRepository and programmingLanguage terms where supported |
| Domains and tasks | [SKOS](https://www.w3.org/TR/skos-reference/) concepts, schemes, labels, alternatives and scope notes |
| Provenance | [PROV-O](https://www.w3.org/TR/prov-o/) entities, activities and source derivation |
| Directed relationships | RDF statements and direct triples generated from one assertion source |
| Contributor account | Custom ContributorAccount with reported historical/recent contribution relationships; no ownership or maintainership claim |
| Hosting account and reported licence | Custom predicates; no verified legal ownership or permission claim |

Absolute URNs derive from case-insensitive GitHub owner/name. The feed has no
immutable ID: transfers/renames currently appear as removal plus addition.
Logical routes identify data records and concepts; they do not promise a
physical Markdown file for every repository. Fully expanded JSON-LD uses no
remote contexts. Shard and build manifests bind the exact source and inputs.

Each relationship retains stable ID, source/target IRIs and routes, predicate,
kind, preferred/inverse labels, status/scope, authority, derivation, observation,
evidence and rights. Source-derived edges are normalised (`normalized`); domain/task edges
are inferred and unreviewed. The schema spelling `normalized` is intentional.
No numeric confidence is invented. Hosting account is not verified service owner.

Evidence includes source URL, frozen path and SHA-256, zero-based source rows,
source field and canonical value hash. Value hashing uses sorted-key compact
UTF-8 JSON with unescaped Unicode and a final newline. Raw hashes cover exact
download bytes. The producer retains sparse and optional source fields in the
frozen source, rather than pretending they are complete.

Independent assurance validates every assertion with Draft 2020-12 JSON
Schema, compares RDF reification with runtime rows and parses every JSON-LD
shard. Ordinary checks cover logical routes, identities, direct triples,
checksums and deterministic rebuilds. These do not establish semantic truth.

SBOM paths are metadata. A future security graph should distinguish repository,
commit, SBOM, package/version, advisory, candidate match and reviewed
applicability, with separate evidence and dates for each.

Content-type suggestions use the same unreviewed name/description rules as
domains and tasks. Contributor relationships instead cite the exact filtered
GitHub observation, account row, date and checksum. Their RDF provenance points
to that observation rather than to the repository feed. The source entities
record both origins. See [history limits](history-and-change.md) and
[facet definitions](rich-facets.md).

Repository graph nodes expose reported historical/recent commit counts, the
recent window, observation time and line-count availability. Contributor
assertions carry their reported count and period in both the runtime and RDF
projection. These are provider observations, not an assessment of contribution
value, software quality or maintainer authority.

Explorer consumes snapshot-bound record locators and per-route assertion
adjacency, with a digest-bound endpoint-label index for readable navigation.
These indexes preserve the custom assertion schema and its authority/evidence
fields; they do not assert canonical rich-runtime conformance. Browser
acceptance and the Pages delivery boundary are described in
[browser acceptance](browser-acceptance.md).
RDF shard paths in the semantic manifest end in .jsonld.gz. Their SHA-256
digests cover the exact compressed bytes; decompress before JSON-LD parsing.
The manifest declares compression, media type and byte length for each shard.

## Lossless assertions and explicit identities

Runtime and RDF assertions retain the same preferred/inverse labels, kind,
source/target routes and IRIs, predicate, status/scope, authority, derivation,
observation, review status, evidence, rights and optional measurement.
Structured authority, evidence, rights and measurement are RDF JSON literals;
derivation and authority-source links remain traversable IRIs. Both independent
assurance and the standalone evaluation verifier compare every assertion.

Vocabulary PredicateUsage nodes carry profile-scoped labels for every predicate,
including external Schema.org predicates. They describe local presentation
without redefining the external predicate's official label or asserting an
`owl:inverseOf` relationship. Inverse adjacency preserves the forward assertion
identity; it does not invent a reverse triple. Logical routes remain stable
and are distinct from physical Markdown storage paths.

The descriptor snapshot_id and semantic manifest build_id identify the complete
bundle. The semantic manifest source_snapshot_iri identifies only the frozen
repository feed; its legacy snapshot field keeps that same source IRI for
compatibility. History and SBOM-quality entities retain content hashes and an
explicit sourceKind. Repository source_metrics expose the exact reported
stargazersCount, forksCount and openIssuesCount, without assigning quality.
