# Licence decisions

Original producer code/documentation are MIT licensed; see LICENSE. This does
not relicense any underlying repository or its code.

The standard repository contract schemas are byte-exact copies from the
owner's OKF Explorer repository, with a checksum lock and canonical schema IDs.
They are validation resources, not a claim to implement the full Bundle Wiki
profile or a new licence for the upstream specification.

The scraper publishes an MIT licence. THIRD_PARTY_NOTICES.md retains its
notice for frozen metadata and copied source evidence. Per-repository licences
are unverified source metadata. Missing licences and NOASSERTION stay
unresolved; public availability alone does not establish reuse permission.

The separately scoped `public-sbom-data-analysis` mode may read SBOM documents
already published at public URLs and match their package data locally. This
operational scope does not itself grant copyright or other reuse rights, and
does not treat public access as permission. Record the source URL, retrieval
date and digest, inspect any stated licence and access terms, and assess the
basis for the proposed analytical reuse before admission. Exclude sources with
restricted access or unresolved reuse terms pending review; do not present
this policy as a legal conclusion or as repository-owner approval for testing.
Keep raw inputs and candidate advisory matches in the private `.sbom-pilot/`
area, outside public builds and archives.

The sample SPDX document declares dataLicense CC0-1.0 for SPDX metadata, not
the dependency code. Preserve underlying package licences. The quality summary
is attributed to its upstream project, not a blanket grant over all software.

Issue titles and repository names identify linked public material. Reports
paraphrase findings. Private reports, credentials, personal contact details
and access-bearing meeting links are outside publication scope.

The owner authorised public editions of the supplied Claude, Gemini and Copilot reports
and their publication on GitHub Pages. Only the reviewed editions in
`docs/ai-evaluations/` and the curated Claude capture review are admitted.
Original reports and raw UI captures remain private. Model/provider names
identify the owner's attribution and make no endorsement claim.
