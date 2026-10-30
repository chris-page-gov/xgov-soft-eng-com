# Credits and upstream contributors

This independent experiment builds on the work of the UK Cross Government
Software Engineering Community and its contributors. Credit does not imply
endorsement, scan permission, legal ownership or current maintainership.

## Repository and SBOM catalogue

The original project is
[uk-x-gov-software-community/xgov-opensource-repo-scraper](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper),
part of the [UK Cross Government Software Engineering Community](https://github.com/uk-x-gov-software-community).
It supplies the published repository feed and upstream SBOM collection and
publication pipeline used as the foundation for this experiment.

The scraper’s recorded human contributors are:

- [Chris Nesbitt-Smith (@chrisns)](https://github.com/chrisns) — 70 recorded commits.
- [Alex Smith (@asmith-nhsx)](https://github.com/asmith-nhsx) — 1 recorded commit.
- [Chris Hyland (@chrishylanduk)](https://github.com/chrishylanduk) — 1 recorded commit.

In particular, acknowledge Chris Nesbitt-Smith’s substantial work on the
repository catalogue and SBOM pipeline. Preserve the original MIT notice in
[third-party notices](THIRD_PARTY_NOTICES.md) when reusing this material.

### Original SBOM implementation evidence

Public commit history and the merged pull request were checked on
30 October 2026. They record Chris Nesbitt-Smith (`@chrisns`) as author of:

| Upstream work | Original evidence |
| --- | --- |
| Initial SBOM collection and CycloneDX commands | [8 March 2026, commit 16d8239](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/commit/16d82394f1b0c9650e529b3a5f4767a5373e66c6) |
| Raw SPDX collection through GitHub's API | [8 March 2026, commit 8684eb5](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/commit/8684eb5b25a3b1f402b1f559abfb547975aeaff3) |
| Separate scheduled SBOM collection workflow | [8 March 2026, commit d5dc579](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/commit/d5dc5795475f5066c06cc00301edf8fad22e115a) |
| Consolidated CycloneDX publication | [16 March 2026, commit f0f8403](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/commit/f0f84033c8152705d4143c9d041564f42af4a0de) |
| Version-resolution and development/runtime scope classification | [PR #40](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/pull/40), [merged commit 21d40c0](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/commit/21d40c08cc33b47de9dccee0fa9ee27c2bf0793c) |

These are recorded authorship statements, not a claim that Git captures every
contribution or establishes sole authorship. Alex Smith and Chris Hyland are
credited above for wider scraper work; the reviewed evidence does not identify
them as authors of these SBOM changes. Original package authors and repository
contributors retain their own credit and licences.

The upstream project collects GitHub dependency-graph SBOM data. This
repository's OKF+ layer and manual, bounded candidate-advisory matching runner
are subsequent additions. The runner uses
[Grype by Anchore and its contributors](https://github.com/anchore/grype);
credit also belongs to the [SPDX](https://github.com/spdx/spdx-spec) and
[CycloneDX](https://github.com/CycloneDX/specification) standards communities.
Tool and format credits do not relicense SBOM data or underlying packages.

## Wider community projects

The following are leading human accounts returned by GitHub, with full
account lists in the [dated inventory](source/contributors-inventory.json).
Fork counts include inherited upstream history; they must not be presented
as work done solely for the community fork.

| Project | Leading recorded human contributors | Source context |
| --- | --- | --- |
| [xgov-opensource-repo-scraper](https://github.com/uk-x-gov-software-community/xgov-opensource-repo-scraper/graphs/contributors) | [Chris Nesbitt-Smith](https://github.com/chrisns) (70), [Alex Smith](https://github.com/asmith-nhsx) (1), [Chris Hyland](https://github.com/chrishylanduk) (1) | Original community repository |
| [uk-x-gov-software-community.github.io](https://github.com/uk-x-gov-software-community/uk-x-gov-software-community.github.io/graphs/contributors) | [Shaun Hare](https://github.com/sdh100shaun) (203), [David Heath](https://github.com/heathd) (60), [Alex Coleman](https://github.com/Sparrow0hawk) (29), [Alex Smith](https://github.com/asmith-nhsx) (9), [@marcotranchino](https://github.com/marcotranchino) (7) | Original community repository |
| [software-developer-learning-pathways-old](https://github.com/uk-x-gov-software-community/software-developer-learning-pathways-old/graphs/contributors) | [David Heath](https://github.com/heathd) (5), [@agamurdoch](https://github.com/agamurdoch) (2) | Original community repository |
| [software-developer-learning-pathways](https://github.com/uk-x-gov-software-community/software-developer-learning-pathways/graphs/contributors) | [Mat](https://github.com/MatMoore) (113), [@deborahchua](https://github.com/deborahchua) (98), [David Heath](https://github.com/heathd) (69), [Kelvin Gan](https://github.com/chao-xian) (10), [George Lund](https://github.com/galund) (7) | Fork of [alphagov/gds-tech-learning-pathway](https://github.com/alphagov/gds-tech-learning-pathway); inherited history included |
| [uk-x-gov-cloud-community](https://github.com/uk-x-gov-software-community/uk-x-gov-cloud-community/graphs/contributors) | [Benjamin Bennett](https://github.com/bendbennett) (19), [@CPHesketh](https://github.com/CPHesketh) (2), [David Heath](https://github.com/heathd) (1) | Original community repository |
| [lean-coffee-hackmd-generator](https://github.com/uk-x-gov-software-community/lean-coffee-hackmd-generator/graphs/contributors) | [David Heath](https://github.com/heathd) (10) | Original community repository |
| [eleventy-plugin-toc](https://github.com/uk-x-gov-software-community/eleventy-plugin-toc/graphs/contributors) | [leah](https://github.com/uncenter) (36), [James Steinbach](https://github.com/jdsteinbach) (7), [Jordan Shurmer](https://github.com/JordanShurmer) (5), [Jon Keeping](https://github.com/JonUK) (3), [Peter deHaan](https://github.com/pdehaan) (1) | Fork of [uncenter/eleventy-plugin-toc](https://github.com/uncenter/eleventy-plugin-toc); inherited history included |
| [uk-x-gov-qa-community.github.io](https://github.com/uk-x-gov-software-community/uk-x-gov-qa-community.github.io/graphs/contributors) | [Ibrahim Jassat](https://github.com/ibrahimjassat) (1) | Original community repository |
| [uk-x-gov-repo-query](https://github.com/uk-x-gov-software-community/uk-x-gov-repo-query/graphs/contributors) | [Shaun Hare](https://github.com/sdh100shaun) (2) | Original community repository |

## How to use these credits

Observed on 28 October 2026 using public default-branch contributor lists and
public profile display names. Counts are GitHub’s recorded commit counts, not
a measure of effort, influence, review, community work or sole authorship.
Anonymous author email records were not requested. Bots and automated accounts
are retained separately in the inventory. No totals are combined across forks.

Link the original repositories and their full contributor pages when presenting
the experiment. Retain source licences and acknowledge design, documentation,
review and community contributions that commit statistics cannot capture.
Confirm preferred attribution and current responsibilities directly before
presenting someone as a maintainer or an approver. No contributor was contacted.
