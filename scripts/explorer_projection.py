"""Bounded, snapshot-bound projections for the existing OKF Explorer contracts."""
import collections
import datetime as dt
import hashlib
import gzip
import io
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote

STOPWORDS = sorted({'a','an','and','as','at','be','by','for','from','in','is','it','of','on','or','the','to','with'})
QUERY_POLICY = {'schema':'okf-search-query-policy.v1','tokeniser':'nfkd-lowercase-ascii-alphanumeric-component-v1','stopwords':STOPWORDS,'minimum_should_match':{'apply_from_query_tokens':1,'minimum_matches':1,'ratio_numerator':1,'ratio_denominator':1}}


def search_tokens(value):
    value = re.sub('[\u0300-\u036f]', '', unicodedata.normalize('NFKD', str(value))).lower()
    return {word for word in re.findall('[a-z0-9]+', value) if len(word)>=2 and word not in STOPWORDS}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else encoded(value)).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def write_gzip(path, value):
    stream = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as zipped:
        zipped.write(encoded(value))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(stream.getvalue())
    return {"path": path.name, "sha256": digest(stream.getvalue()), "bytes": len(stream.getvalue()), "compression": "gzip"}


def bucket(route):
    """Match Explorer's FNV-1a hash of the ASCII, percent-encoded local route."""
    value = 2166136261
    for char in route:
        if ord(char) > 127:
            raise ValueError("Explorer routes must be percent encoded")
        value = ((value ^ ord(char)) * 16777619) & 0xffffffff
    return f"{value:08x}"[:2]


def reader_activity(profile):
    result = {key: value for key, value in profile.items() if key != "contributors"}
    result["contributors"] = [{key: value for key, value in actor.items() if key != "weeks"} for actor in profile["contributors"]]
    annual = collections.defaultdict(lambda: [0, 0, 0])
    for actor in profile["contributors"]:
        for timestamp, commits, additions, deletions in actor["weeks"]:
            year = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).year
            values = annual[year]
            values[0] += commits
            values[1] += additions
            values[2] += deletions
    result["annual_totals"] = [[year, *values] for year, values in sorted(annual.items())]
    return result


def text(value):
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]").replace("\n", " ")


def narrative(record):
    lines = [record["body"], "", "## Code activity and contributor history", "", "History coverage: " + record["history_coverage"] + "."]
    activity = record.get("activity")
    if not activity:
        lines += ["", "Statistics are not available in this snapshot. This does not mean no activity or no contributors."]
        if record.get('history_observation'):
            lines += ['', 'Provider state: '+record['history_coverage']+'. Reason: '+record['history_observation']['reason_code']+'.']
    else:
        window = activity["window"]
        lines += ["", f"GitHub reports **{activity['historical_reported_commits']:,} historical commits** and **{activity['recent_reported_commits']:,} recent commits**.", "", f"Recent means {window['label']}: {window['start']} to {window['end_exclusive']} (end excluded).", "", "| Contributor account | Historical reported commits | Recent reported commits |", "| --- | ---: | ---: |"]
        for actor in activity["contributors"]:
            label = "@" + actor["login"] if actor.get("login") else "Unmapped account"
            lines.append(f"| {text(label)} | {actor['historical_reported_commits']:,} | {actor['recent_reported_commits']:,} |")
        has_lines = activity["line_count_status"] != "unknown-or-omitted-by-api"
        lines += ["", "### Historical change", "", "Rows group the provider's weeks by the year of their UTC start date. Counts can include inherited fork history and generated files.", "", "| Year of week start | Reported commits | Reported additions | Reported deletions |", "| --- | ---: | ---: | ---: |"]
        for year, commits, additions, deletions in activity["annual_totals"]:
            lines.append(f"| {year} | {commits:,} | {format(additions, ',') if has_lines else 'Unknown'} | {format(deletions, ',') if has_lines else 'Unknown'} |")
        lines += ["", "### Recent weekly change", "", "| Week starting (UTC) | Reported commits | Reported additions | Reported deletions |", "| --- | ---: | ---: | ---: |"]
        for timestamp, commits, additions, deletions in activity["weekly_totals"]:
            day = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).date().isoformat()
            lines.append(f"| {day} | {commits:,} | {format(additions, ',') if has_lines else 'Unknown'} | {format(deletions, ',') if has_lines else 'Unknown'} |")
        lines += ["", "Line-count availability: " + activity["line_count_status"] + ".", "", "Observation: " + activity["source"]["observed_at"] + ".", "", "Captured observation SHA-256: `" + activity["source"]["sha256"] + "`. The frozen observation is included in the downloadable archive.", "", "GitHub statistics exclude merge and empty commits. Counts do not establish quality, ownership, maintainership, security or scan permission."]
        if activity['source'].get('catalogue_binding'):
            lines += ['', 'Catalogue join: '+activity['source']['catalogue_binding']+'. '+activity['source']['join_basis']+'. The history observation and catalogue can have different collection dates and source hashes.']
    lines += ["", "## Catalogue metadata change", "", "Status: " + record["metadata_change"] + ".", "", "Changed source fields: " + (", ".join(record["metadata_changed_fields"]) or "none reported, or no comparable baseline") + ".", "", "Metadata changes are separate from code changes. See the collection coverage before interpreting a missing value as zero."]
    return {"title": "Repository activity, contributors and evidence", "body": "\n".join(lines)}


def project(output, records, concepts, edges, snapshot, observed, profile):
    output = Path(output)
    search = read(output / "data/search/manifest.json")
    search["snapshot"] = snapshot
    search['query_policy'] = QUERY_POLICY
    write(output / "data/search/manifest.json", search)
    manifest = read(output / "data/manifest.json")
    descriptor = read(output / "okf-explorer.json")
    manifest["snapshot"] = snapshot

    locations = collections.defaultdict(dict)
    size = search["result_doc_chunk_size"]
    for ordinal, record in enumerate(records):
        locations[bucket(record["route"])][record["route"]] = [ordinal // size, ordinal % size]
    locator_paths = {}
    for key, rows in sorted(locations.items()):
        path = f"data/record-locator/{key}.json"
        write(output / path, rows)
        locator_paths[key] = path
    def resource_binding(path):
        raw = (output / path).read_bytes()
        return {"path": path, "sha256": digest(raw), "bytes": len(raw), **({"compression":"gzip"} if path.endswith(".gz") else {})}

    locator = {"schema": "okf-record-locator-sharded.v1", "algorithm": "fnv1a32-prefix-2", "snapshot": snapshot, "records": len(records), "chunk_size": size, "record_chunks": [resource_binding(path) for path in manifest["chunks"]["datasets"]], "buckets": {key: resource_binding(path) for key, path in locator_paths.items()}, "bucket_count": len(locator_paths)}
    write(output / "data/record-locator.json", locator)

    adjacency = collections.defaultdict(lambda: collections.defaultdict(list))
    for edge in edges:
        for route in set((edge["source"], edge["target"])):
            adjacency[bucket(route)][route].append(edge)
    adjacency_paths = {}
    for key, rows in sorted(adjacency.items()):
        path = f"data/adjacency/{key}.json.gz"
        packed_binding = write_gzip(output / path, rows)
        adjacency_paths[key] = packed_binding | {"path": path}
    write(output / "data/adjacency.json", {"algorithm": "fnv1a32-prefix-2", "snapshot": snapshot, "buckets": adjacency_paths})

    labels = [{"route": record["route"], "iri": record["id"], "label": record["title"], "type": "Repository"} for record in records]
    aliases = {}
    for concept in concepts.values():
        route = concept.get("urn:okf:xgov:route")
        if route:
            kind = route.split("/", 1)[0]
            label_type = {"contributors": "Contributor account", "account": "Hosting account", "sbom": "SBOM reference", "language": "Language", "licence": "Reported licence", "domains": "Subject domain", "capabilities": "Engineering task", "content-types": "Content type"}.get(kind, "Concept")
            label = concept["http://www.w3.org/2004/02/skos/core#prefLabel"]
            entry = {"route": route, "iri": concept["@id"], "label": label, "type": label_type}
            labels.append(entry)
            value = unquote(route.split("/", 1)[1][:-3])
            if kind in ("language", "licence"):
                value = label
            for alias_kind in {"account": ["publisher"], "language": ["language", "format"], "licence": ["license"], "domains": ["domain"], "capabilities": ["capability"]}.get(kind, []):
                alias = alias_kind + "/" + quote(value, safe="~")
                aliases[alias] = route
                labels.append(entry | {"route": alias})
    locator["route_aliases"] = aliases
    write(output / "data/record-locator.json", locator)
    if len(labels) > 100000:
        raise ValueError("Endpoint label contract exceeds the Explorer's 100,000-entry ceiling")
    for label in labels:
        label.update(language="en-GB", label_authority={"class": "editorial", "source": profile})
    write(output / "data/endpoint-labels.json", {"schema": "okf-explorer-endpoint-label-index.v1", "snapshot": snapshot, "generated_at": observed, "default_language": "en-GB", "opaque_identifier_patterns": [], "entries": labels, "counts": {"entries": len(labels)}})

    for name, path in {"record_locator": "data/record-locator.json", "relationship_adjacency": "data/adjacency.json", "endpoint_labels": "data/endpoint-labels.json"}.items():
        raw = (output / path).read_bytes()
        reference = {"path": path, "sha256": digest(raw), "bytes": len(raw)}
        descriptor["entrypoints"][name] = reference
        manifest["indexes"][name] = reference
    manifest["shards"] = {name: [resource_binding(path) for path in manifest["chunks"][name]] for name in ("datasets", "relationships")}
    roots = {name: digest({path: digest((output / path).read_bytes()) for path in manifest["chunks"][name]}) for name in ("datasets", "relationships")}
    descriptor["plane_roots"] = roots
    descriptor["exploratory_publication"] = {"schema": "okf-exploratory-publication.v1", "publication_state": "exploratory", "snapshot_id": snapshot, "generated_at": observed, "applicable_plane_roots": roots, "publisher": {"name": "Independent cross-government software discovery experiment", "url": "https://github.com/chris-page-gov/xgov-soft-eng-com", "authority_status": "independent-research"}, "banner": {"label": "Exploratory", "message": "This is an incomplete research view, not an authoritative service or released data product. Content and links may change. Check the cited official source before making a decision.", "feedback_url": "https://github.com/chris-page-gov/xgov-soft-eng-com/issues/new", "preserve_route": True}, "indexing_policy": "noindex", "limitations": ["Classifications are unreviewed name and description matches.", "GitHub history coverage is partial and does not establish maintainership.", "No estate-wide vulnerability assessment is provided."], "permitted_claims": ["Public metadata can be explored with source provenance."], "prohibited_claims": ["Do not claim official endorsement, exhaustive coverage or security assurance."], "promotion_rule": "Any stronger publication claim requires a separate owner decision and supporting evidence."}
    if descriptor.get('history_coverage'):
        descriptor['exploratory_publication']['limitations'].append(descriptor['history_coverage']['message'])
    write(output / "data/manifest.json", manifest)
    write(output / "okf-explorer.json", descriptor)


def validate(output, records, edges):
    """Replay every record location, incident assertion and declared binding."""
    output = Path(output)
    descriptor = read(output / "okf-explorer.json")
    snapshot = descriptor["snapshot_id"]
    manifest = read(output / "data/manifest.json")
    search = read(output / "data/search/manifest.json")
    if manifest.get("snapshot") != snapshot or search.get("snapshot") != snapshot:
        raise ValueError("Explorer projection snapshot mismatch")
    for name in ("record_locator", "relationship_adjacency", "endpoint_labels"):
        reference = descriptor["entrypoints"][name]
        if manifest["indexes"][name] != reference:
            raise ValueError("Explorer projection binding mismatch")
        raw = (output / reference["path"]).read_bytes()
        if digest(raw) != reference["sha256"] or len(raw) != reference["bytes"]:
            raise ValueError("Explorer projection integrity mismatch")
    locator = read(output / descriptor["entrypoints"]["record_locator"]["path"])
    if locator['records'] != len(records) or len(locator['record_chunks']) != len(manifest['chunks']['datasets']):
        raise ValueError('Record locator chunk or record count differs')
    locations = {}
    for reference in locator["buckets"].values():
        raw = (output / reference["path"]).read_bytes()
        if digest(raw) != reference["sha256"] or len(raw) != reference["bytes"]:
            raise ValueError("Record locator bucket integrity mismatch")
        locations.update(json.loads(raw))
    expected = {row["route"]: [i // locator["chunk_size"], i % locator["chunk_size"]] for i, row in enumerate(records)}
    if locations != expected:
        raise ValueError("Record locator does not cover every repository exactly")
    for chunk_index, (reference, path) in enumerate(zip(locator["record_chunks"], manifest["chunks"]["datasets"])):
        raw = (output / path).read_bytes()
        if reference["path"] != path or digest(raw) != reference["sha256"] or len(raw) != reference["bytes"]:
            raise ValueError("Record chunk integrity mismatch")
        for row_index, record in enumerate(read(output / path)):
            if locations.get(record['route']) != [chunk_index,row_index]:
                raise ValueError('Record locator does not replay the actual record chunk')
    expected_edges = collections.defaultdict(dict)
    for edge in edges:
        for route in set((edge["source"], edge["target"])):
            expected_edges[route][edge["id"]] = digest(edge)
    adjacency = read(output / descriptor["entrypoints"]["relationship_adjacency"]["path"])
    actual = {}
    for prefix, reference in adjacency["buckets"].items():
        raw = (output / reference["path"]).read_bytes()
        if digest(raw) != reference["sha256"] or len(raw) != reference["bytes"]:
            raise ValueError("Relationship adjacency integrity mismatch")
        rows = json.loads(gzip.decompress(raw))
        for route, values in rows.items():
            if bucket(route) != prefix or len(values) != len({row["id"] for row in values}):
                raise ValueError("Relationship adjacency has an invalid bucket or duplicate")
            actual[route] = {row["id"]: digest(row) for row in values}
    if dict(expected_edges) != actual:
        raise ValueError("Relationship adjacency lost assertion data")
    labels = read(output / descriptor["entrypoints"]["endpoint_labels"]["path"])
    routes = [row["route"] for row in labels["entries"]]
    if len(routes) != len(set(routes)) or not set(expected_edges).issubset(routes):
        raise ValueError("Relationship endpoints lack unique readable labels")
    if descriptor["exploratory_publication"]["applicable_plane_roots"] != descriptor["plane_roots"]:
        raise ValueError("Exploratory publication roots differ")
    for name, declared in descriptor["plane_roots"].items():
        if digest({path: digest((output / path).read_bytes()) for path in manifest["chunks"][name]}) != declared:
            raise ValueError("Explorer plane integrity root differs")
    return True
