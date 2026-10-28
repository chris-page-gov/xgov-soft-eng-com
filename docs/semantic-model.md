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
| Catalogue and frozen metadata | [DCAT 3](https://www.w3.org/TR/vocab-dcat-3/) Catalog and Dataset |
| Repository | Custom Repository, with [Schema.org](https://schema.org/SoftwareSourceCode) name, description, codeRepository and programmingLanguage terms where supported |
| Domains and tasks | [SKOS](https://www.w3.org/TR/skos-reference/) concepts, schemes, labels, alternatives and scope notes |
| Provenance | [PROV-O](https://www.w3.org/TR/prov-o/) entities, activities and source derivation |
| Directed relationships | RDF statements and direct triples generated from one assertion source |
| Hosting account and reported licence | Custom predicates; no verified legal ownership or permission claim |

Absolute URNs derive from case-insensitive GitHub owner/name. The feed has no
immutable ID: transfers/renames currently appear as removal plus addition.
Logical routes identify data records and concepts; they do not promise a
physical Markdown file for every repository. Fully expanded JSON-LD uses no
remote contexts. Shard and build manifests bind the exact source and inputs.

Each relationship retains stable ID, source/target IRIs and routes, predicate,
kind, preferred/inverse labels, status/scope, authority, derivation, observation,
evidence and rights. Source-derived edges are normalized; domain/task edges
are inferred and unreviewed. The schema spelling normalized is intentional.
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
