"""Complete, evidence-labelled facet values and distinct-record counts."""
import collections
import datetime as dt

METRICS=("packages","resolved","unresolved","runtime","excludedDev","excludedUnresolved","excludedCi")
LANGUAGE_FAMILIES={"JavaScript":"javascript-typescript","TypeScript":"javascript-typescript","Python":"python","Jupyter Notebook":"notebooks","Java":"jvm","Scala":"jvm","Kotlin":"jvm","C#":"dotnet","F#":"dotnet","Visual Basic .NET":"dotnet","Ruby":"ruby","Go":"go","Rust":"rust","PHP":"php","R":"r","HCL":"infrastructure-language","Shell":"shell","PowerShell":"shell","HTML":"web-markup-style","CSS":"web-markup-style","SCSS":"web-markup-style","C":"c-cpp","C++":"c-cpp","SQL":"sql"}


def quality_rows(report):
    if not isinstance(report,dict) or not isinstance(report.get("perRepo"),list) or not report["perRepo"]:raise ValueError("SBOM quality report must contain perRepo rows")
    stamp=dt.datetime.fromisoformat(report["generatedAt"].replace("Z","+00:00"))
    if stamp.tzinfo is None:raise ValueError("SBOM quality generation timestamp needs a timezone")
    result={};totals=collections.Counter()
    for row in report["perRepo"]:
        if not isinstance(row,dict) or not isinstance(row.get("repo"),str) or row["repo"].count("/")!=1:raise ValueError("Invalid SBOM quality repository identity")
        for key in METRICS:
            if type(row.get(key)) is not int or row[key]<0:raise ValueError("Invalid SBOM quality count")
            totals[key]+=row[key]
        if row["resolved"]+row["unresolved"]!=row["packages"] or row["runtime"]+row["excludedDev"]+row["excludedUnresolved"]+row["excludedCi"]!=row["packages"] or row["runtime"]>row["resolved"]:raise ValueError("SBOM quality counts do not reconcile")
        identity=row["repo"].casefold()
        if identity in result and result[identity]!=row:raise ValueError("Conflicting duplicate SBOM quality rows")
        result[identity]=row
    if any(report.get("totals",{}).get(k)!=v for k,v in totals.items()):raise ValueError("SBOM quality totals do not reconcile with published rows")
    return result


def analysis_values(record,quality,observed_at,quality_generated_at=None):
    language=record["language"]
    values={"language_family":LANGUAGE_FAMILIES.get(language,"unknown" if language=="unknown" else "other-reported-language"),"licence_status":"unresolved" if record["license_id"] in ("unknown","NOASSERTION") else "identifier-reported-unverified","description_status":"supplied" if record["description"] else "not-supplied","fork_status":"unknown" if record["is_fork"] is None else str(record["is_fork"]).lower()}
    if record.get("timestamp"):
        age=(observed_at-dt.datetime.fromisoformat(record["timestamp"].replace("Z","+00:00"))).days
        values["push_age"]="future-date" if age<0 else "0-90-days" if age<=90 else "91-365-days" if age<=365 else "1-3-years" if age<=1095 else "over-3-years"
        values["push_year"]=record["timestamp"][:4]
    else:values.update(push_age="unknown",push_year="unknown")
    if quality is None:
        values.update(sbom_resolution="not-reported",package_volume="not-reported",dependency_context=["not-reported"],quality_report_age="not-reported")
        return values
    count=quality["packages"]
    values["sbom_resolution"]="empty-reported-inventory" if not count else "all-reported-versions-resolved" if quality["unresolved"]==0 else "none-resolved" if quality["resolved"]==0 else "some-unresolved"
    values["package_volume"]="0" if count==0 else "1-20" if count<=20 else "21-100" if count<=100 else "101-500" if count<=500 else "501-2000" if count<=2000 else "over-2000"
    values["dependency_context"]=[label for condition,label in ((quality["runtime"]>0,"runtime-candidates-reported"),(quality["excludedDev"]>0,"build-test-candidates-reported"),(quality["excludedCi"]>0,"ci-candidates-reported"),(quality["unresolved"]>0,"unresolved-versions-reported")) if condition] or ["empty-reported-inventory"]
    age=(observed_at-dt.datetime.fromisoformat(quality_generated_at.replace("Z","+00:00"))).total_seconds()
    values["quality_report_age"]="future-report-time" if age<0 else "within-48-hours-of-snapshot" if age<=172800 else "older-than-48-hours-at-snapshot"
    return values


def facet_values(record,spec):
    value=record.get(spec["field"])
    if value is None or value==[] or value=="":return [spec["missing_value"]]
    values=value if isinstance(value,list) else [value]
    return sorted({str(v).lower() if isinstance(v,bool) else str(v) for v in values})


def counts(records,specs):
    output={}
    for spec in specs:
        counter=collections.Counter(value for record in records for value in facet_values(record,spec))
        output[spec["key"]]=[{"value":v,"label":spec.get("value_labels",{}).get(v,v),"count":n} for v,n in sorted(counter.items(),key=lambda item:(-item[1],item[0]))]
    return output


def validate(records,specs,emitted):
    if counts(records,specs)!=emitted:raise ValueError("Facet counts disagree with complete record classifications")
    for spec in specs:
        if any(spec["field"] not in record for record in records):raise ValueError("Incomplete facet record population: "+spec["key"])
        if spec.get("required_task_dimension"):
            meaningful={v for row in records for v in facet_values(row,spec) if v!=spec["missing_value"]}
            selections={tuple(facet_values(row,spec)) for row in records}
            if len(meaningful)<2 or len(selections)<2:raise ValueError("Required task facet does not distinguish records")
    return True
