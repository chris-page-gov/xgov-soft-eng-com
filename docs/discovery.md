# Improve discovery

Let people start with a problem, narrow the evidence and inspect candidate
repositories. Search rank expresses term matches, not trust or recommendations.

| Need | Implemented behaviour | Evidence boundary |
| --- | --- | --- |
| Find a task | Token search and optional task-vocabulary expansion | Name/description rules retain matched terms |
| Explore a subject | Multiple proposed domain labels and unclassified buckets | Unreviewed labels; no official classification claim |
| Narrow candidates | Account, language, licence, archive, fork, domain and task filters | Unknowns remain; archived material is included by default |
| Understand a result | Match reasons, row positions and field hashes | No invented confidence score |
| Inspect reuse | Source URL, reported licence and metadata gaps | No legal clearance, security or support assurance |
| Track changes | Added, removed and changed identities after a baseline exists | Disappearance is not proof of deletion |

The initial 24,137 rows reduce to 24,068 distinct GitHub repository URLs. All
69 duplicate pairs are identical. Quality checks use distinct-record
denominators and retain raw counts separately. Source update, code push,
HTTP Last-Modified and retrieval dates describe different events.

config/taxonomy.json proposes 20 subject domains and 15 engineering tasks.
Whole normalised tokens/phrases match names and descriptions only; an account
name never assigns all its repositories to a domain. Review ambiguous terms,
false matches and unclassified groups with domain specialists. A zero count
does not establish absence of relevant code.

Next priorities:

1. Admit guidance and standards as a distinct source family with rights,
   authority and freshness; the repository feed does not include every link
   on the community resources page.
2. Enrich an agreed sample with READMEs, topics, maintainers and immutable IDs.
3. Evaluate tasks such as address components, accessible forms, API clients,
   maintained components and package-to-repository impact discovery.
4. Add reviewed hierarchies, aliases and cross-domain relationships. Similarity
   must not become identity, dependency or substitutability.
5. Complete Explorer browser, graph and performance acceptance before
   advertising a verified browser discovery URL.

The upstream uk-x-gov-repo-query already implements lightweight metadata
filters. Reuse its learning and keep interoperability explicit.
