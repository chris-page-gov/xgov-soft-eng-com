#!/usr/bin/env python3
"""Frozen-source OKF+ producer and explainable, local catalogue search (stdlib only)."""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import tomllib
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import facets as facet_tools
import explorer_projection

ROOT = Path(__file__).resolve().parents[1]
NS = "urn:okf:xgov:"
SCHEMA = "https://schema.org/"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
SKOS = "http://www.w3.org/2004/02/skos/core#"
PROV = "http://www.w3.org/ns/prov#"
DCAT = "http://www.w3.org/ns/dcat#"
DCT = "http://purl.org/dc/terms/"
PROFILE = "https://github.com/chris-page-gov/xgov-soft-eng-com/blob/main/docs/semantic-model.md"
SCHEMES=("domains","capabilities","content_types")


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else encoded(value)).hexdigest()


def read(path):
    return explorer_projection.read(path)


def write(path, value):
    path = Path(path)
    if path.suffix == '.gz':
        explorer_projection.write_gzip(path,value)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def normalise(value):
    return " ".join(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", str(value)).casefold()))


def iri(kind, value):
    return NS + kind + ":" + urllib.parse.quote(str(value).casefold(), safe="")


def route(kind, value):
    return kind.replace('_','-') + "/" + urllib.parse.quote(str(value).casefold(), safe="") + ".md"


def ref(value):
    return {"@id": value}


def validate_source(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("Source must be a non-empty JSON array")
    groups = collections.defaultdict(list)
    for pos, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"Row {pos}: expected object")
        for key in ("owner", "name", "url"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Row {pos}: missing or invalid {key}")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", row["owner"]) or not re.fullmatch(r"[A-Za-z0-9_.-]+", row["name"]):
            raise ValueError(f"Row {pos}: unsafe GitHub identity")
        expected = f"https://github.com/{row['owner']}/{row['name']}"
        if row["url"].casefold() != expected.casefold():
            raise ValueError(f"Row {pos}: URL and identity disagree")
        if type(row.get("archived")) is not bool:
            raise ValueError(f"Row {pos}: archived must be a boolean")
        if row.get("isFork") is not None and type(row["isFork"]) is not bool:
            raise ValueError(f"Row {pos}: isFork must be a boolean or absent")
        for key in ("description", "language", "sbom"):
            if row.get(key) is not None and not isinstance(row[key], str):
                raise ValueError(f"Row {pos}: invalid {key}")
        licence = row.get("license")
        if licence is not None:
            if not isinstance(licence, dict) or any(licence.get(k) is not None and not isinstance(licence[k], str) for k in ("key", "name", "spdxId", "url")):
                raise ValueError(f"Row {pos}: invalid licence metadata")
        for key in ("createdAt", "updatedAt", "pushedAt"):
            if row.get(key) is not None:
                parse_date(row[key])
        for key in ("stargazersCount", "forksCount", "openIssuesCount"):
            if type(row.get(key)) is not int or row[key] < 0:
                raise ValueError(f"Row {pos}: invalid {key}")
        sbom = row.get("sbom")
        if sbom and (not re.fullmatch(r"sbom/[A-Za-z0-9_.\-/]+\.json\.gz", sbom) or ".." in sbom.split("/")):
            raise ValueError(f"Row {pos}: unsafe SBOM path")
        groups[row["url"].casefold()].append((pos, row))
    unique, duplicates = [], []
    for url, group in sorted(groups.items()):
        if any(item != group[0][1] for _, item in group[1:]):
            raise ValueError(f"Conflicting duplicate: {url}; curator review required")
        positions = [p for p, _ in group]
        unique.append((group[0][1], positions))
        if len(group) > 1:
            duplicates.append({"url": url, "positions": positions, "policy": "identical-rows-collapsed"})
    return unique, duplicates


def parse_date(value):
    stamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Timestamp requires a timezone")
    return stamp


def classify(row, taxonomy):
    text = " " + normalise(row["name"] + " " + (row.get("description") or "")) + " "
    matches = {}
    for scheme in SCHEMES:
        matches[scheme] = []
        for concept in taxonomy.get(scheme,[]):
            hits = [term for term in concept["terms"] if " " + normalise(term) + " " in text]
            if hits:
                matches[scheme].append({"id": concept["id"], "label": concept["label"], "matched_terms": hits})
    return matches


def controlled_inputs(root):
    patterns = ["config/**/*", "scripts/**/*.py", "scripts/**/*.js", "tests/**/*.py", "schemas/**/*", "docs/**/*", "*.md", "okf.*.json", "pyproject.toml", "uv.lock", "requirements-assurance.txt", "LICENSE", ".gitignore", ".python-version", ".github/workflows/*", ".githooks/*", "source/README.md", "source/security-helper-inventory.json", "source/contributors-inventory.json", "source/history/index.json", "source/upstream/*", "source/sbom-review/*"]
    return {p.relative_to(root).as_posix(): digest(p.read_bytes()) for pattern in patterns for p in sorted(root.glob(pattern)) if p.is_file() and "__pycache__" not in p.parts and p.name!=".DS_Store"}


def stale(receipt, hours, at=None):
    return ((at or dt.datetime.now(dt.timezone.utc)) - parse_date(receipt["retrieved_at"])).total_seconds() > hours * 3600


def build(root, output, receipt, previous=None):
    cfg, tax = read(root / "config/catalogue.json"), read(root / "config/taxonomy.json")
    raw_path = root / receipt["path"]
    raw_bytes = raw_path.read_bytes()
    if digest(raw_bytes) != receipt["sha256"]:
        raise ValueError("Frozen source checksum mismatch")
    rows = json.loads(raw_bytes)
    unique, duplicates = validate_source(rows)
    observed, snapshot = receipt["retrieved_at"], NS + "snapshot:" + receipt["sha256"]
    quality_receipt=receipt.get("supplements",{}).get("sbom-quality")
    quality_report=None;quality_index={}
    if quality_receipt:
        quality_bytes=(root/quality_receipt["path"]).read_bytes()
        if digest(quality_bytes)!=quality_receipt["sha256"]:raise ValueError("SBOM quality source checksum mismatch")
        quality_report=json.loads(quality_bytes);quality_index=facet_tools.quality_rows(quality_report)
    facet_specs=read(root/"config/facets.json")["facets"]
    facet_observed=max(parse_date(observed),parse_date(quality_receipt["retrieved_at"]) if quality_receipt else parse_date(observed))
    history_index=read(root/'source/history/index.json') if (root/'source/history/index.json').exists() else {'repositories':{}}
    history_sources=[]
    for item in history_index['repositories'].values():
        if not re.fullmatch(r'source/history/observations/[0-9a-f]{64}\.json',item['path']) or digest((root/item['path']).read_bytes())!=item['sha256']:raise ValueError('Invalid history source binding')
        history_sources.append({'path':item['path'],'sha256':item['sha256']})
    prior_summary={}
    if receipt.get('baseline_summary'):
        baseline=receipt['baseline_summary'];data=(root/baseline['path']).read_bytes()
        if digest(data)!=baseline['sha256']:raise ValueError('Metadata baseline checksum mismatch')
        prior_summary=json.loads(data)
    record_summary={}
    inputs = controlled_inputs(root)
    build_id = digest({"inputs": inputs, "receipt": receipt, "baseline_sha256": digest(previous or {})})
    output.mkdir(parents=True, exist_ok=True)
    record_nodes, records, edges, concepts, facets = [], [], [], {}, collections.defaultdict(collections.Counter)
    counts = collections.Counter()
    source_licence = cfg["source_licence"]
    rights = {"source": source_licence, "assertion": "Source repository reports MIT; repository licences are separate and unverified. No assurance of reuse permission."}
    predicates = {
        "account": (NS + "hostingAccount", "hosted under account", "hosts repository", "owner"),
        "language": (SCHEMA + "programmingLanguage", "reports primary language", "reported primary language of", "language"),
        "licence": (NS + "reportedLicence", "reports licence identifier", "reported licence of", "license"),
        "sbom": (NS + "reportedSbom", "reports SBOM reference", "reported SBOM reference of", "sbom"),
        "domains": (SCHEMA + "about", "suggested domain", "suggested domain of", "name+description"),
        "capabilities": (NS + "suggestedCapability", "suggested capability", "suggested capability of", "name+description")}
    predicates["content_types"]=(NS+"suggestedContentType","suggested content type","suggested content type of","name+description")
    predicates["historical_contributor"]=(NS+'reportedHistoricalContributor','historical contributor reported by GitHub','reported historical contributor to','profile.contributors')
    predicates["recent_contributor"]=(NS+'reportedRecentContributor','recent contributor reported by GitHub','reported recent contributor to','profile.contributors')
    predicates["domain-parent"] = (SKOS + "broader", "broader concept", "narrower concept", "config/taxonomy.json")
    for scheme in SCHEMES:
        scheme_id = iri("scheme", scheme)
        concepts[scheme_id] = {"@id": scheme_id, "@type": SKOS + "ConceptScheme", SKOS + "prefLabel": scheme.capitalize()}
        for c in tax.get(scheme,[]):
            ci = iri(scheme, c["id"])
            concepts[ci] = {"@id": ci, "@type": SKOS + "Concept", SKOS + "prefLabel": c["label"], SKOS + "altLabel": c["terms"], SKOS + "inScheme": ref(scheme_id), SKOS + "scopeNote": tax["policy"], NS + "route": route(scheme, c["id"])}
    for row, positions in unique:
        identity = row["owner"] + "/" + row["name"]
        ri, rr = iri("repository", identity), route("repositories", identity)
        matches = classify(row, tax)
        history_item=history_index['repositories'].get(identity.casefold())
        history_observation=read(root/history_item['path']) if history_item else None
        activity=history_observation.get('profile') if history_observation else None
        actor_evidence={}
        licence = (row.get("license") or {}).get("spdxId") or "unknown"
        n = {"@id": ri, "@type": NS + "Repository", SCHEMA + "name": identity, SCHEMA + "codeRepository": ref(row["url"]), PROV + "wasDerivedFrom": ref(snapshot), NS + "route": rr, NS + "archived": row["archived"], NS + "isFork": row.get("isFork"), NS + "sourceRows": positions}
        if row.get("description"):
            n[SCHEMA + "description"] = row["description"]
        for source_key, target_key in (("createdAt", "created"), ("updatedAt", "metadataUpdated"), ("pushedAt", "codePushed"), ("stargazersCount", "stars"), ("forksCount", "forks"), ("openIssuesCount", "openIssues")):
            n[NS + target_key] = row.get(source_key)
        related = [("account", row["owner"], row["owner"], [])]
        if row.get("language"):
            related.append(("language", row["language"], row["language"], []))
        if licence != "unknown":
            related.append(("licence", licence, licence, []))
        if row.get("sbom"):
            related.append(("sbom", row["sbom"], "SBOM reference for "+identity, []))
        for scheme in SCHEMES:
            for hit in matches[scheme]:
                related.append((scheme, hit["id"], hit["label"], hit["matched_terms"]))
        if activity:
            for position,actor in enumerate(activity['contributors']):
                if not actor.get('login'):continue
                for kind,count in (('historical_contributor',actor['historical_reported_commits']),('recent_contributor',actor['recent_reported_commits'])):
                    if count:
                        related.append((kind,actor['login'],'@'+actor['login'],[]));actor_evidence[(kind,actor['login'])]=(position,actor)
        for kind, value, label, terms in related:
            target, tr = iri(kind, value), route(kind, value)
            if kind in ('historical_contributor','recent_contributor'):target,tr=iri('contributor',value),route('contributors',value)
            if target not in concepts:
                concepts[target] = {"@id": target, "@type": NS + "HostingAccount" if kind == "account" else NS + "SbomReference" if kind == "sbom" else SKOS + "Concept", SKOS + "prefLabel": label, NS + "route": tr}
                if kind == "sbom":
                    concepts[target][SCHEMA+"contentUrl"] = ref(urllib.parse.urljoin(cfg["source_url"],value))
                    concepts[target][NS+"verificationStatus"] = "source-reported-reference-not-fetched-by-build"
                if kind in ('historical_contributor','recent_contributor'):concepts[target]['@type']=NS+'ContributorAccount'
            pred, preferred, inverse, field = predicates[kind]
            inferred = kind in SCHEMES
            status = "inferred" if inferred else "normalized"
            assertion_id = NS + "assertion:" + digest([ri, pred, target])
            evidence_value = {k: row.get(k) for k in ("name", "description")} if inferred else row.get(field)
            evidence = {"url": cfg["source_url"], "source_artifact": receipt["path"], "source_sha256": receipt["sha256"], "rows": positions, "source_field": field, "source_value_sha256": digest(evidence_value), "matched_terms": terms}
            edge = {"id": assertion_id, "source": rr, "target": tr, "source_iri": ri, "target_iri": target, "predicate": pred, "kind": kind, "label": preferred, "inverse_label": inverse, "assertion_status": status, "assertion_scope": "real-world", "authority": {"class": "derived", "label": "Experimental catalogue projection", "source": cfg["source_url"]}, "derivation": iri("rule", "term-match-v1" if inferred else "source-field-v1"), "observed_at": observed, "evidence": [evidence], "rights": rights, "review_status": "unreviewed" if inferred else "source-reported-not-independently-verified"}
            if (kind,value) in actor_evidence:
                position,actor=actor_evidence[(kind,value)]
                edge['authority']['source']=history_observation['source_url'];edge['observed_at']=history_observation['observed_at']
                edge['evidence']=[{'url':history_observation['source_url'],'source_artifact':history_item['path'],'source_sha256':history_item['sha256'],'rows':[position],'source_field':'profile.contributors','source_value_sha256':digest(actor),'matched_terms':[]}]
                edge['rights']={'source':'https://docs.github.com/en/site-policy/github-terms/github-terms-of-service','assertion':'Public GitHub statistics; no ownership, maintainership, endorsement or scan authority asserted.'}
                edge['measurement']={'reported_commits':actor['recent_reported_commits'] if kind=='recent_contributor' else actor['historical_reported_commits'],'period':'recent-complete-weeks' if kind=='recent_contributor' else 'available-provider-history'}
                if kind=='recent_contributor':edge['measurement'].update(window_start=activity['window']['start'],window_end_exclusive=activity['window']['end_exclusive'])
            edges.append(edge)
            n.setdefault(pred, []).append(ref(target))
        domains = [h["id"] for h in matches["domains"]] or ["unclassified"]
        capabilities = [h["id"] for h in matches["capabilities"]] or ["unclassified"]
        rec = {"id": ri, "name": identity.casefold(), "title": identity, "route": rr, "concept_id": rr, "record_type": "Repository", "type": "Repository", "publisher": row["owner"].casefold(), "publisher_title": row["owner"], "publisher_concept_id": route("account", row["owner"]), "notes": row.get("description") or "", "description": row.get("description") or "", "url": row["url"], "open": rr, "resource": row["url"], "resource_count": 0, "formats": [row["language"]] if row.get("language") else [], "language": row.get("language") or "unknown", "license_id": licence, "license_title": (row.get("license") or {}).get("name") or "Unknown", "license_basis": "source-reported-unverified" if licence not in ("unknown", "NOASSERTION") else "unresolved", "archived": row["archived"], "is_fork": row.get("isFork"), "timestamp": row.get("pushedAt"), "metadata_modified": row.get("updatedAt"), "metadata_created": row.get("createdAt"), "domains": domains, "capabilities": capabilities, "topics": domains, "tags": capabilities, "classification_evidence": matches, "source_rows": positions, "provenance": {"source_sha256": receipt["sha256"], "observed_at": observed, "source_url": cfg["source_url"], "authority": "catalogue-metadata"}, "sbom_url": urllib.parse.urljoin(cfg["source_url"], row["sbom"]) if row.get("sbom") else None, "quality_gaps": [key for key in ("description", "language", "license", "isFork") if row.get(key) in (None, "")], "body": f"# {identity}\n\n{row.get('description') or 'No description supplied.'}\n\nCatalogue metadata only. Classification suggestions are unreviewed. Inspect the source repository before reuse."}
        records.append(rec)
        record_nodes.append(n)
        rec["sbom"] = "present" if row.get("sbom") else "not-reported"
        rec["content_types"]=[h["id"] for h in matches["content_types"]] or ["unclassified"]
        quality_row=quality_index.get(identity.casefold())
        rec.update(facet_tools.analysis_values(rec,quality_row,facet_observed,quality_report["generatedAt"] if quality_report else None))
        rec["sbom_quality"]={"counts":quality_row,"generated_at":quality_report["generatedAt"],"source":quality_receipt} if quality_row else None
        rec['history_coverage']=history_item['state'] if history_item else 'not-collected'
        rec['historical_contributors']=[a['login'] for a in activity['contributors'] if a.get('login') and a['historical_reported_commits']] if activity else ['not-collected']
        rec['recent_contributors']=[a['login'] for a in activity['contributors'] if a.get('login') and a['recent_reported_commits']] if activity else ['not-collected']
        if activity:
            count=activity['recent_reported_commits'];rec['recent_commit_band']='0' if count==0 else '1-10' if count<=10 else '11-50' if count<=50 else '51-200' if count<=200 else 'over-200'
            rec['recent_contributors']=rec['recent_contributors'] or ['no-mapped-account' if count else 'none-reported-in-window'];rec['historical_contributors']=rec['historical_contributors'] or ['no-mapped-account']
            rec['churn_availability']=activity['line_count_status'];rec['activity']=explorer_projection.reader_activity(activity)|{'source':history_item|{'observed_at':history_observation['observed_at']}}
            n[PROV+'wasDerivedFrom']=[ref(snapshot),ref(NS+'snapshot:'+history_item['sha256'])]
            for key,value in {'reportedRecentCommitCount':activity['recent_reported_commits'],'reportedHistoricalCommitCount':activity['historical_reported_commits'],'activityWindowStart':activity['window']['start'],'activityWindowEndExclusive':activity['window']['end_exclusive'],'activityObservedAt':history_observation['observed_at'],'lineCountStatus':activity['line_count_status']}.items():n[NS+key]=value
            if activity['recent_reported_line_changes'] is not None:n[NS+'reportedRecentLineChanges']=activity['recent_reported_line_changes']
        else:rec.update(recent_commit_band='not-collected',churn_availability='not-collected',activity=None)
        record_summary[ri]=row
        older=prior_summary.get(ri);changed=[k for k in sorted(set(row)|set(older or {})) if older is not None and row.get(k)!=older.get(k)]
        rec['metadata_changed_fields']=changed
        rec['metadata_change']='baseline-unavailable' if not prior_summary else 'added' if older is None else 'changed' if changed else 'unchanged'
        rec['metadata_change_degree']='baseline-unavailable' if not prior_summary else 'new-record' if older is None else '0-fields' if not changed else '1-field' if len(changed)==1 else '2-4-fields' if len(changed)<=4 else '5-or-more-fields'
        rec['narrative']=explorer_projection.narrative(rec)
        for key, values in {"publisher": [rec["publisher"]], "language": [rec["language"]], "license": [licence], "archived": [str(row["archived"]).lower()], "is_fork": ["unknown" if row.get("isFork") is None else str(row["isFork"]).lower()], "domain": domains, "capability": capabilities, "sbom": [rec["sbom"]]}.items():
            facets[key].update(values)
        for key in ("description", "language", "license", "isFork"):
            counts["missing_" + key] += row.get(key) in (None, "")
        counts["unresolved_licences"] += licence in ("unknown","NOASSERTION")
        counts["archived"] += row["archived"]
        counts["sbom_paths"] += bool(row.get("sbom"))
    size = cfg["chunk_size"]
    chunk_paths = []
    semantic_paths, edge_paths = [], []
    for part, offset in enumerate(range(0, len(records), size)):
        p = f"data/records-{part:03d}.json.gz"
        write(output / p, records[offset:offset + size]); chunk_paths.append(p)
        p = f"semantic/repositories-{part:03d}.jsonld.gz"
        write(output / p, {"@graph": record_nodes[offset:offset + size]}); semantic_paths.append(p)
    # Reification and direct triples originate from the same edge rows; planes remain explicit.
    for part, offset in enumerate(range(0, len(edges), size)):
        batch = edges[offset:offset + size]
        p = f"data/assertions-{part:03d}.json.gz"
        write(output / p, batch); edge_paths.append(p)
        graph = []
        for e in batch:
            graph.append({"@id": e["id"], "@type": [RDF + "Statement", PROV + "Entity", NS + "RelationshipAssertion"], RDF + "subject": ref(e["source_iri"]), RDF + "predicate": ref(e["predicate"]), RDF + "object": ref(e["target_iri"]), PROV + "wasDerivedFrom": ref(NS+'snapshot:'+e['evidence'][0]['source_sha256']), PROV + "wasGeneratedBy": ref(NS + "build:" + build_id), NS + "assertionStatus": e["assertion_status"], NS + "assertionScope": e["assertion_scope"], NS + "evidence": {"@value": e["evidence"], "@type": RDF + "JSON"}, NS + "rights": e['rights']["assertion"]})
            if e.get('measurement'):
                graph[-1][NS+'reportedCommitCount']=e['measurement']['reported_commits']
                graph[-1][NS+'measurement']={'@value':e['measurement'],'@type':RDF+'JSON'}
        p = f"semantic/assertions-{part:03d}.jsonld.gz"
        write(output / p, {"@graph": graph}); semantic_paths.append(p)
    rdfs="http://www.w3.org/2000/01/rdf-schema#"
    definitions=[{"@id":NS+name,"@type":rdfs+"Class",rdfs+"label":label} for name,label in (("Repository","Source-reported GitHub repository"),("HostingAccount","Source-reported hosting account"),("ContributorAccount","Public contributor account reported by GitHub"),("SbomReference","Source-reported SBOM reference"),("RelationshipAssertion","Evidence-bearing relationship assertion"))]
    definitions += [{"@id":p,"@type":RDF+"Property",rdfs+"label":label} for p,label,_,_ in predicates.values() if p.startswith(NS)]
    write(output / "semantic/vocabulary.jsonld.gz", {"@graph": list(concepts.values())+definitions})
    write(output / "semantic/catalogue.jsonld", {"@graph": [{"@id": NS + "catalogue", "@type": DCAT + "Catalog", DCT + "title": "Experimental cross-government software catalogue", PROV + "wasDerivedFrom": ref(snapshot)}, {"@id": snapshot, "@type": [DCAT + "Dataset", PROV + "Entity"], DCT + "source": ref(cfg["source_url"]), PROV + "generatedAtTime": observed, NS + "sha256": receipt["sha256"], NS + "httpLastModified": receipt.get("last_modified")}, {"@id": NS + "build:" + build_id, "@type": PROV + "Activity", PROV + "used": ref(snapshot), NS + "inputHashes": {"@value": inputs, "@type": RDF + "JSON"}}]})
    source_graph=read(output/'semantic/catalogue.jsonld')['@graph']
    for extra in ([quality_receipt] if quality_receipt else [])+history_sources:
        source_graph.append({'@id':NS+'snapshot:'+extra['sha256'],'@type':PROV+'Entity',NS+'sha256':extra['sha256'],NS+'sourceArtifact':extra['path']})
    write(output/'semantic/catalogue.jsonld',{'@graph':source_graph})
    semantic_paths += ["semantic/vocabulary.jsonld.gz", "semantic/catalogue.jsonld"]
    write(output / "semantic/manifest.json", {"profile": PROFILE, "snapshot": snapshot, "context_policy": "fully-expanded-IRIs-no-remote-contexts", "shards": [{"path": p, "sha256": digest((output / p).read_bytes()), "bytes": (output/p).stat().st_size, "media_type": "application/ld+json", **({"compression":"gzip"} if p.endswith(".gz") else {})} for p in semantic_paths]})
    counts.update({"raw_rows": len(rows), "records": len(records), "datasets": len(records), "duplicate_rows": len(rows)-len(records), "organisations": len(facets["publisher"]), "relationships": len(edges), "resources": 0, "publishers": len(facets["publisher"]), "unclassified_domains": facets["domain"]["unclassified"], "unclassified_capabilities": facets["capability"]["unclassified"]})
    warnings = ["Experimental metadata discovery; classifications are unreviewed term matches.", "Hosting accounts are not verified legal organisations or service owners.", "Missing licences and NOASSERTION do not establish reuse permission.", "Pushed dates, stars, SBOM paths and archive flags do not establish quality, security or support.", "The repository feed does not contain all guidance linked from the community resources page.", "The source fetch time and HTTP Last-Modified do not verify every upstream record was refreshed."]
    for spec in facet_specs:
        scheme={"domain":"domains","capability":"capabilities","content_type":"content_types"}.get(spec["key"])
        if scheme:spec["value_labels"]={c["id"]:c["label"] for c in tax.get(scheme,[])}|{"unclassified":"Unclassified"}
    facet_payload=facet_tools.counts(records,facet_specs)
    facet_tools.validate(records,facet_specs,facet_payload)
    write(output/"data/facet-definitions.json",{"schema":"xgov-facet-contract.v1","facets":facet_specs,"consumer":"catalogue.py search/facets; OKF Explorer with recorded Chrome acceptance"})
    write(output/"data/presentation.json",{"schema":"okf-explorer-presentation.v1","status":"experimental","facets":[{"key":s["key"],"label":s["label"],"description":s["description"],"value_type":"nominal","order":i*10,"default_state":"pinned" if s.get("required_task_dimension") else "shown","open_control":"search" if s["key"] in ("publisher","language","license") else "distribution","value_order":"count-desc","examples":[r["label"] for r in facet_payload[s["key"]][:3]]} for i,s in enumerate(facet_specs)]})
    write(output / "data/facets.json", facet_payload)
    overview = {"schema": "okf-large-overview.v1", "title": "Cross-government software discovery", "generated_at": observed, "counts": dict(counts), "warnings": warnings, "facet_previews": {k: v[:15] for k,v in facet_payload.items()}, "recent_datasets": sorted(records, key=lambda r: r["timestamp"] or "", reverse=True)[:10]}
    write(output / "data/overview.json", overview)
    write(output / "quality.json", {"grain": "unique case-insensitive GitHub repository URL", "counts": dict(counts), "duplicates": duplicates, "source_fields": dict(collections.Counter(k for row in rows for k in row)), "warnings": warnings})
    previous_map = previous or {}
    current_map = {r["id"]: digest({k:v for k,v in r.items() if k not in ("provenance", "source_rows")}) for r in records}
    # Changes compare normalised records with the prior successfully admitted snapshot.
    changes = {"baseline_available": bool(previous_map), "added": sorted(set(current_map)-set(previous_map)) if previous_map else [], "removed": sorted(set(previous_map)-set(current_map)), "changed": sorted(k for k in set(current_map)&set(previous_map) if current_map[k]!=previous_map[k])}
    write(output / "changes.json", changes)
    write(output / "record-hashes.json", current_map)
    write(output/'record-summary.json',record_summary)
    build_search(output, records, facet_payload, size)
    publishers = [{"id": c["@id"], "name": c[SKOS+"prefLabel"].casefold(), "title": c[SKOS+"prefLabel"], "concept_id": c[NS+"route"], "type": "Hosting account"} for c in concepts.values() if c["@type"] == NS+"HostingAccount"]
    write(output / "data/accounts.json", publishers)
    manifest = {"title": "Experimental cross-government software catalogue", "generated_at": observed, "counts": dict(counts), "indexes": {"overview": "data/overview.json", "search": "data/search/manifest.json", "facets": "data/facets.json"}, "chunks": {"datasets": chunk_paths, "resources": [], "publishers": ["data/accounts.json"], "relationships": edge_paths}}
    write(output / "data/manifest.json", manifest)
    descriptor = {"schema": "okf-explorer-large-corpus.v1", "kind": "okf-large-corpus", "okf_version": "0.2", "title": "Experimental cross-government software OKF+", "description": "Source-reported repository metadata with explicit gaps and unreviewed domain and task suggestions.", "version": tomllib.loads((root/'pyproject.toml').read_text())['project']['version'], "publication_state": "exploratory", "status": "local-experiment", "profile": PROFILE, "snapshot_id": build_id, "generated_at": observed, "counts": dict(counts), "entrypoints": {"data_manifest": "data/manifest.json", "overview_index": "data/overview.json", "search_manifest": "data/search/manifest.json", "markdown_index": "index.md"}, "source": {"url": cfg["source_url"], "source_sha256": receipt["sha256"], "observed_at": observed}, "semantic_descriptor": "semantic/manifest.json", "vocabulary": {"record_singular": "repository", "record_plural": "repositories", "publisher_singular": "hosting account", "publisher_plural": "hosting accounts", "format_plural": "languages"}, "warnings": warnings}
    write(output / "okf-explorer.json", descriptor)
    descriptor["entrypoints"].update(presentation="data/presentation.json",facet_definitions="data/facet-definitions.json")
    descriptor["extensions"]={"okf-explorer-presentation.v1":{"mode":"external","entrypoint":"presentation"}}
    write(output/"okf-explorer.json",descriptor)
    (output / "index.md").write_text('---\nokf_version: "0.2"\n---\n# Experimental cross-government software OKF+\n\n'+f'{len(records):,} distinct repositories from {len(facets["publisher"])} hosting accounts.\n\n'+"\n".join("- "+w for w in warnings)+"\n\n[Domains and tasks](concepts/index.md) · [Source quality](quality.json) · [Semantic graph](semantic/manifest.json)\n")
    links = []
    for scheme in SCHEMES:
        for c in tax.get(scheme,[]):
            p = output / "concepts" / scheme / (c["id"]+".md")
            p.parent.mkdir(parents=True, exist_ok=True)
            count=next((r["count"] for r in facet_payload[{"domains":"domain","capabilities":"capability","content_types":"content_type"}[scheme]] if r["value"]==c["id"]),0)
            p.write_text('---\ntype: Concept\ntitle: '+json.dumps(c["label"])+ '\nstatus: experimental\n---\n# '+c["label"]+f'\n\n{count:,} repositories match the experimental name/description rules.\n\nTerms: '+", ".join(c["terms"])+".\n\nMatches are suggestions, with evidence in each record. A zero count does not establish absence.\n")
            links.append(f'- [{c["label"]}]({scheme}/{c["id"]}.md)')
    (output / "concepts/index.md").write_text("# Domains and tasks\n\n"+"\n".join(links)+"\n")
    (output / "README.md").write_text("# Generated catalogue\n\nRebuild with `python scripts/catalogue.py build`. Do not edit these files by hand.\n")
    explorer_projection.project(output,records,concepts,edges,build_id,observed,PROFILE)
    write(output / "build-manifest.json", {"schema": "xgov-build.v1", "build_id": build_id, "baseline_sha256":digest(previous or {}), "generated_at": observed, "source": receipt, "history_sources":history_sources, "controlled_inputs": inputs, "outputs": {p.relative_to(output).as_posix(): digest(p.read_bytes()) for p in sorted(output.rglob("*")) if p.is_file() and p.name!='.DS_Store'}})
    return dict(counts)


def build_search(output, records, facets, size):
    postings = collections.defaultdict(dict)
    docs = []
    filter_values = collections.defaultdict(lambda: collections.defaultdict(list))
    specifications=read(output/"data/facet-definitions.json")["facets"]
    for ordinal, record in enumerate(records):
        doc = {**{key:value for key,value in record.items() if key not in ('body','narrative','activity','sbom_quality','classification_evidence')}, "ordinal": ordinal, "quality_score": None}
        docs.append(doc)
        for field, text, weight, mask in (("title", record["title"], 16, 1), ("publisher", record["publisher_title"], 8, 2), ("description", record["notes"], 5, 8), ("topics", " ".join(record["domains"]), 3, 16), ("tags", " ".join(record["capabilities"]), 3, 32)):
            for token in explorer_projection.search_tokens(text):
                if len(token) >= 2:
                    old = postings[token].get(ordinal, [0, 0])
                    postings[token][ordinal] = [old[0]+weight, old[1]|mask]
        for spec in specifications:
            key=spec["key"]
            for v in facet_tools.facet_values(record,spec):
                filter_values[key][v].append(ordinal)
    lex, shards, prefixes = collections.defaultdict(list), collections.defaultdict(dict), collections.defaultdict(dict)
    for token, matches in sorted(postings.items()):
        shard = (token[:2] if re.fullmatch(r"[a-z0-9]{2}", token[:2]) else "__")
        p = f"data/search/postings/{shard}.json"
        lex[shard].append({"token": token, "df": len(matches), "postings": p})
        shards[shard][token] = [[i, score, mask] for i,(score,mask) in sorted(matches.items())]
        for length in range(3,min(8,len(token))+1):
            prefixes[shard].setdefault(token[:length], []).append({"token":token,"df":len(matches)})
    for shard in lex:
        write(output / f"data/search/lexicon/{shard}.json", lex[shard])
        write(output / f"data/search/postings/{shard}.json", {"tokens":shards[shard]})
        write(output / f"data/search/prefixes/{shard}.json", {p:sorted(v,key=lambda r:(-r['df'],r['token']))[:16] for p,v in prefixes[shard].items()})
    paths=[]
    for part, offset in enumerate(range(0,len(docs),size)):
        p=f"data/search/results-{part:03d}.json.gz";write(output/p,docs[offset:offset+size]);paths.append(p)
    write(output/"data/search/doc-map.json",{str(i):r["route"] for i,r in enumerate(records)})
    write(output/"data/search/sort-values.json",[[r["timestamp"] or '',r["title"],None] for r in records])
    for key, values in filter_values.items():
        write(output/f"data/search/filters/{key}.json",{"schema":"okf-static-filter-postings.v1","key":key,"values":dict(values)})
    write(output/"data/search/manifest.json",{"schema":"okf-static-search.v2","token_min_length":2,"prefix_min_length":3,"lexicon_shard_length":2,"result_limit":200,"result_doc_chunk_size":size,"weights":{"title":16,"publisher":8,"description":5,"topics":3,"tags":3},"field_masks":{"title":1,"publisher":2,"description":8,"topics":16,"tags":32},"counts":{"documents":len(records),"tokens":len(postings),"postings":sum(len(v) for v in postings.values())},"entrypoints":{"lexicon":{s:f"data/search/lexicon/{s}.json" for s in lex},"prefixes":{s:f"data/search/prefixes/{s}.json" for s in lex},"postings":[f"data/search/postings/{s}.json" for s in lex],"result_docs":paths,"facets":"data/facets.json","doc_map":"data/search/doc-map.json","sort_values":"data/search/sort-values.json","filter_postings":{key:f"data/search/filters/{key}.json" for key in filter_values}}})


def load_receipt(root):
    return read(root / "source/current.json")


def records_from(output):
    manifest=read(output/"data/manifest.json")
    return [r for p in manifest["chunks"]["datasets"] for r in read(output/p)]


def remove_build_tree(path):
    """Retry only a Finder-metadata race; propagate other cleanup failures."""
    for attempt in range(3):
        try:
            shutil.rmtree(path)
            return
        except OSError as exc:
            if exc.errno not in (39,66) or attempt==2:raise
            failed=Path(exc.filename) if exc.filename else path
            if not failed.resolve().is_relative_to(path.resolve()):raise
            if any(p.name!='.DS_Store' for p in failed.iterdir()):raise
            for metadata in failed.glob('.DS_Store'):
                metadata.unlink(missing_ok=True)


def promote(root, receipt, baseline=None):
    if (root/"generated/build-manifest.json").exists():
        old_inputs=read(root/"generated/build-manifest.json")["controlled_inputs"]
        new_inputs=controlled_inputs(root)
        implementation=lambda p: p.startswith(("scripts/","config/","schemas/","tests/",".github/")) or p in ("pyproject.toml","uv.lock","okf.semantic.json","okf.publication.json")
        changed=any(old_inputs.get(p)!=new_inputs.get(p) for p in set(old_inputs)|set(new_inputs) if implementation(p))
        if changed and old_inputs.get("CHANGELOG.md")==new_inputs.get("CHANGELOG.md"):
            raise ValueError("Controlled implementation changed: update CHANGELOG.md and relevant documentation before rebuilding")
    parent=root/".build";parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as name:
        candidate=Path(name)/"generated"
        build(root,candidate,receipt,baseline)
        check_output(candidate)
        old=root/".build/previous-generated"
        if old.exists():remove_build_tree(old)
        if (root/"generated").exists():os.replace(root/"generated",old)
        try:os.replace(candidate,root/"generated")
        except BaseException:
            if old.exists():os.replace(old,root/"generated")
            raise
        if old.exists():remove_build_tree(old)
    write(root/"source/current.json",receipt)


def check_output(output):
    manifest=read(output/"build-manifest.json")
    for path, checksum in manifest["outputs"].items():
        if digest((output/path).read_bytes())!=checksum:raise ValueError(f"Output checksum mismatch: {path}")
    records=records_from(output)
    facet_tools.validate(records,read(output/"data/facet-definitions.json")["facets"],read(output/"data/facets.json"))
    routes={r["route"]:r["id"] for r in records}
    concepts=read(output/"semantic/vocabulary.jsonld.gz")["@graph"]
    routes.update({c[NS+"route"]:c["@id"] for c in concepts if NS+"route" in c})
    nodes={n["@id"]:n for p in read(output/"semantic/manifest.json")["shards"] if p["path"].startswith("semantic/repositories-") for n in read(output/p["path"])["@graph"]}
    seen=set()
    all_edges=[]
    data_manifest=read(output/"data/manifest.json")
    for p in data_manifest["chunks"]["relationships"]:
        for edge in read(output/p):
            if edge["id"] in seen:raise ValueError("Duplicate assertion ID")
            seen.add(edge["id"])
            all_edges.append(edge)
            if routes.get(edge["source"])!=edge["source_iri"] or routes.get(edge["target"])!=edge["target_iri"]:raise ValueError("Unresolved semantic route")
            if ref(edge["target_iri"]) not in nodes[edge["source_iri"]].get(edge["predicate"],[]):raise ValueError("Direct triple and assertion disagree")
            if edge["assertion_status"] not in ("normalized","inferred"):raise ValueError("Unexpected authority plane")
            if not edge["evidence"] or not edge["rights"]:raise ValueError("Missing evidence or rights")
    if len(records)!=len({r['id'] for r in records}):raise ValueError("Duplicate repository identity")
    if len(seen)!=read(output/"quality.json")["counts"]["relationships"]:raise ValueError("Assertion total mismatch")
    explorer_projection.validate(output,records,all_edges)
    return {"records":len(records),"assertions":len(seen),"outputs":len(manifest["outputs"])}


def fetch(root):
    cfg=read(root/"config/catalogue.json")
    req=urllib.request.Request(cfg["source_url"],headers={"User-Agent":"xgov-software-okf/0.1 (public metadata research)","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=cfg["timeout_seconds"]) as response:
        if response.geturl()!=cfg["source_url"]:raise ValueError("Source redirect requires review")
        raw=response.read(cfg["max_bytes"]+1)
        if len(raw)>cfg["max_bytes"]:raise ValueError("Source exceeds size limit")
        unique,_=validate_source(json.loads(raw))
        if len(unique)<cfg["minimum_records"]:raise ValueError("Source unexpectedly small")
        previous=read(root/"generated/record-hashes.json") if (root/"generated/record-hashes.json").exists() else {}
        removed=set(previous)-{iri("repository",r['owner']+'/'+r['name']) for r,_ in unique}
        if previous and len(removed)/len(previous)>cfg["maximum_removal_fraction"]:raise ValueError("Large removal requires curator review; current build retained")
        checksum=digest(raw)
        path=f"source/snapshots/{checksum}.json"
        dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists() and dest.read_bytes()!=raw:raise ValueError("Snapshot identity collision")
        dest.write_bytes(raw)
        receipt={"path":path,"sha256":checksum,"bytes":len(raw),"url":cfg["source_url"],"retrieved_at":now(),"last_modified":response.headers.get("Last-Modified"),"etag":response.headers.get("ETag")}
        if (root/"source/current.json").exists() and load_receipt(root)["sha256"]==checksum:
            receipt=load_receipt(root)
            previous=read(root/receipt["baseline_path"]) if receipt.get("baseline_path") else {}
        else:
            receipt["baseline_path"]=f"source/baselines/{checksum}.json"
            write(root/receipt["baseline_path"],previous)
        receipt=dict(receipt)
        if (root/'generated/record-summary.json').exists():
            summary=read(root/'generated/record-summary.json');summary_hash=digest(summary);path=f'source/baselines/{summary_hash}.summaries.json';write(root/path,summary)
            receipt['baseline_summary']={'path':path,'sha256':summary_hash}
        if cfg.get("sbom_quality_url"):
            old=load_receipt(root).get("supplements",{}).get("sbom-quality") if (root/"source/current.json").exists() else None
            receipt["supplements"]={"sbom-quality":fetch_quality(root,cfg,old)}
        promote(root,receipt,previous)
        write(root/"source/last-check.json",{"checked_at":now(),"source_sha256":checksum,"result":"validated-and-promoted"})
        return {"source_sha256":checksum,"records":len(unique),"refreshed":True}


def fetch_quality(root,cfg,old=None):
    url=cfg["sbom_quality_url"]
    req=urllib.request.Request(url,headers={"User-Agent":"xgov-software-okf/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=cfg["timeout_seconds"]) as response:
        if response.geturl()!=url:raise ValueError("SBOM quality source redirect requires review")
        raw=response.read(cfg["max_bytes"]+1)
        if len(raw)>cfg["max_bytes"]:raise ValueError("SBOM quality report exceeds size limit")
        report=json.loads(raw);facet_tools.quality_rows(report)
        checksum=digest(raw)
        if old and old["sha256"]==checksum:return old
        path=f"source/snapshots/{checksum}.sbom-quality.json"
        destination=root/path;destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists() and destination.read_bytes()!=raw:raise ValueError("SBOM quality identity collision")
        destination.write_bytes(raw)
        return {"path":path,"sha256":checksum,"bytes":len(raw),"url":url,"retrieved_at":now(),"generated_at":report["generatedAt"],"last_modified":response.headers.get("Last-Modified")}


def search(records, query, taxonomy, filters=None, include_inferred=True):
    terms=normalise(query).split()
    synonyms={}
    expansions=[]
    if include_inferred:
        q=" "+normalise(query)+" "
        for scheme in SCHEMES:
            for c in taxonomy.get(scheme,[]):
                hits=[t for t in c["terms"] if " "+normalise(t)+" " in q]
                if hits:
                    synonyms[c["id"]]=c["label"]
                    expansions.append((c["id"],set(normalise(" ".join(hits)).split())))
    results=[]
    for r in records:
        def allowed(key,requested):
            wanted=requested if isinstance(requested,list) else [requested]
            actual=r.get(key);actual=actual if isinstance(actual,list) else ["unknown" if actual is None else actual]
            return bool({str(v).casefold() for v in wanted}&{str(v).casefold() for v in actual})
        if any(not allowed(key,value) for key,value in (filters or {}).items()):continue
        text=normalise(r["title"]+" "+r["description"])
        words=set(text.split())
        direct=all(t in words for t in terms)
        matched=sorted(set(synonyms)&set(r["domains"]+r["capabilities"]+r.get("content_types",[]))) if terms else []
        explained=set().union(*(tokens for concept,tokens in expansions if concept in matched)) if matched else set()
        if terms and not direct and (not matched or any(t not in words and t not in explained for t in terms)):continue
        score=sum(4 for t in terms if t in normalise(r["title"]).split())+sum(t in words for t in terms)+(1 if matched else 0)
        results.append({"score":score,"title":r["title"],"url":r["url"],"language":r["language"],"licence":r["license_id"],"archived":r["archived"],"reason":"all query tokens in source name/description" if direct and terms else "suggested concepts: "+", ".join(synonyms[k] for k in matched) if matched else "facet match", "source_rows":r["source_rows"],"classification_evidence":r["classification_evidence"] if matched else {}})
    return sorted(results,key=lambda r:(-r["score"],r["title"].casefold()))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=ROOT)
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("refresh",help="Download, validate, build and promote the public feed")
    sub.add_parser("build",help="Rebuild from frozen inputs, without network access")
    sub.add_parser("check",help="Verify every output and deterministic documentation lockstep")
    sub.add_parser("status",help="Report source observation and retrieval freshness")
    f=sub.add_parser("facets",help="Facet counts within the current search and filter selection")
    f.add_argument("--query",default="");f.add_argument("--facet");f.add_argument("--limit",type=int,default=20);f.add_argument("--offset",type=int,default=0);f.add_argument("--value-query",default="");f.add_argument("--json",action="store_true");f.add_argument("--source-only",action="store_true")
    q=sub.add_parser("search");q.add_argument("query",nargs="?",default="");q.add_argument("--limit",type=int,default=10)
    for name in ("organisation","language","licence","domain","capability","archived","is-fork","sbom","content-type","language-family","licence-status","push-age","push-year","description-status","sbom-resolution","dependency-context","package-volume","quality-report-age","history-coverage","recent-commit-band","churn-availability","recent-contributor","historical-contributor","metadata-change","metadata-change-degree"):
        q.add_argument("--"+name,action="append");f.add_argument("--"+name,action="append")
    q.add_argument("--source-only",action="store_true",help="Do not expand queries through inferred concepts")
    q.add_argument("--json",action="store_true")
    args=parser.parse_args();root=args.root.resolve()
    try:
        if args.command=="refresh":result=fetch(root)
        elif args.command=="build":
            receipt=load_receipt(root)
            promote(root,receipt,read(root/receipt["baseline_path"]) if receipt.get("baseline_path") else {})
            result=check_output(root/"generated")
        elif args.command=="check":
            result=check_output(root/"generated")
            receipt=load_receipt(root)
            baseline=read(root/receipt["baseline_path"]) if receipt.get("baseline_path") else {}
            with tempfile.TemporaryDirectory() as name:
                output=Path(name)/"generated";build(root,output,load_receipt(root),baseline)
                expected={p.relative_to(output).as_posix():digest(p.read_bytes()) for p in output.rglob("*") if p.is_file() and p.name!=".DS_Store"}
                actual={p.relative_to(root/"generated").as_posix():digest(p.read_bytes()) for p in (root/"generated").rglob("*") if p.is_file() and p.name!=".DS_Store"}
                if expected!=actual:raise ValueError("Generated outputs or documentation lockstep are stale; run build after reviewing source and documentation changes")
            result["deterministic_lockstep"]="passed"
        elif args.command=="status":
            receipt=load_receipt(root);cfg=read(root/"config/catalogue.json")
            last=read(root/"source/last-check.json") if (root/"source/last-check.json").exists() else {}
            result={"source":receipt,"last_check":last,"retrieval_stale":stale({"retrieved_at":last.get("checked_at",receipt["retrieved_at"])},cfg["stale_after_hours"]),"upstream_record_freshness":"not-independently-verified","publication":"configured-github-releases-and-pages-remote-state-not-checked","scheduler":"configured-daily-1643-UTC-remote-state-not-checked"}
        else:
            filters={k:v for k,v in {"publisher":args.organisation,"language":args.language,"license_id":args.licence,"domains":args.domain,"capabilities":args.capability,"archived":args.archived,"is_fork":args.is_fork,"sbom":args.sbom}.items() if v is not None}
            filters.pop("is_fork",None)
            if args.is_fork:filters["fork_status"]=args.is_fork
            for flag,field in (("content_type","content_types"),("language_family","language_family"),("licence_status","licence_status"),("push_age","push_age"),("push_year","push_year"),("description_status","description_status"),("sbom_resolution","sbom_resolution"),("dependency_context","dependency_context"),("package_volume","package_volume"),("quality_report_age","quality_report_age"),("history_coverage","history_coverage"),("recent_commit_band","recent_commit_band"),("churn_availability","churn_availability"),("recent_contributor","recent_contributors"),("historical_contributor","historical_contributors"),("metadata_change","metadata_change"),("metadata_change_degree","metadata_change_degree")):
                if getattr(args,flag):filters[field]=getattr(args,flag)
            population=records_from(root/"generated")
            rows=search(population,args.query,read(root/"config/taxonomy.json"),filters,not args.source_only)
            if args.command=="facets":
                selected={r["url"] for r in rows};counts=facet_tools.counts([r for r in population if r["url"] in selected],read(root/"generated/data/facet-definitions.json")["facets"])
                if args.facet:
                    if args.facet not in counts:raise ValueError("Unknown facet key")
                    counts={args.facet:counts[args.facet]}
                if args.value_query:counts={k:[r for r in v if normalise(args.value_query) in normalise(r["label"]+" "+r["value"])] for k,v in counts.items()}
                print(json.dumps({"selected_records":len(selected),"facet_value_totals":{k:len(v) for k,v in counts.items()},"facets":{k:v[max(0,args.offset):max(0,args.offset)+max(0,args.limit)] for k,v in counts.items()},"overlap_policy":"OR within a facet; AND across facets. Counts are distinct repositories per value; multi-value counts are not additive."},indent=2));return
            result={"total_matches":len(rows),"results":rows[:max(0,min(args.limit,200))],"status": "experimental-unreviewed-classification"}
            if not args.json:
                print(f"{len(rows):,} matches; showing {len(result['results'])}.")
                for r in result["results"]:print(f"{r['title']} | {r['language']} | {r['licence']} | archived={r['archived']}\n  {r['url']}\n  {r['reason']}")
                return
        print(json.dumps(result,indent=2,ensure_ascii=False))
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print(f"Catalogue operation failed: {exc}",file=sys.stderr);sys.exit(1)


if __name__=="__main__":main()
