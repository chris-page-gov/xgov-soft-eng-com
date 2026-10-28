#!/usr/bin/env python3
"""Independent JSON Schema and RDF parsing assurance; no remote context loading."""
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker
from rdflib import Graph
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import catalogue as c


def main():
    out = ROOT / "generated"
    result = c.check_output(out)
    schema_lock=c.read(ROOT/"schemas/standard-lock.json")
    resources=[]
    for path,checksum in schema_lock["files"].items():
        if c.digest((ROOT/path).read_bytes())!=checksum:raise ValueError("Standard schema checksum mismatch")
        schema=c.read(ROOT/path);resources.append((schema["$id"],Resource.from_contents(schema)))
    registry=Registry().with_resources(resources)
    for contract,schema_path in schema_lock["contracts"].items():
        Draft202012Validator(c.read(ROOT/schema_path),registry=registry,format_checker=FormatChecker()).validate(c.read(ROOT/contract))
    result["standard_repository_contracts_validated"]=len(schema_lock["contracts"])
    validator = Draft202012Validator(c.read(ROOT / "schemas/assertion.schema.json"), format_checker=FormatChecker())
    total = 0
    for path in c.read(out / "data/manifest.json")["chunks"]["relationships"]:
        rows=c.read(out/path)
        semantic=c.read(out/path.replace("data/assertions-", "semantic/assertions-").replace(".json", ".jsonld"))["@graph"]
        if len(rows)!=len(semantic):raise ValueError("Reification row count disagrees")
        for row,node in zip(rows,semantic):
            validator.validate(row)
            expected={"@id":row["id"],c.RDF+"subject":c.ref(row["source_iri"]),c.RDF+"predicate":c.ref(row["predicate"]),c.RDF+"object":c.ref(row["target_iri"]),c.NS+"assertionStatus":row["assertion_status"],c.PROV+"wasDerivedFrom":c.ref(c.NS+'snapshot:'+row['evidence'][0]['source_sha256'])}
            if row.get('measurement'):expected[c.NS+'reportedCommitCount']=row['measurement']['reported_commits']
            if any(node[k]!=v for k,v in expected.items()):raise ValueError("RDF reification and runtime assertion disagree")
            total+=1
    triples=0
    for shard in c.read(out/"semantic/manifest.json")["shards"]:
        raw=(out/shard["path"]).read_bytes()
        if c.digest(raw)!=shard["sha256"]:raise ValueError("RDF shard checksum mismatch")
        document=json.loads(raw)
        if "@context" in document:raise ValueError("Unexpected context: expanded IRIs required")
        graph=Graph().parse(data=raw.decode(),format="json-ld")
        triples+=len(graph)
    result.update({"draft_2020_12_assertions_validated":total,"rdf_triples_parsed_across_shards":triples,"remote_contexts":0})
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
