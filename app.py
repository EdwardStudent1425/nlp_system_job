from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/"src"))
import streamlit as st
from jobmatch.extraction import extract_local, parse_cv, redact_contacts, validate_profile
from jobmatch.models import Preferences, Job, Profile, Recommendation
from jobmatch.sources import load_jobs, fetch_dou
from jobmatch.search import SearchIndex
from jobmatch.export import export_results
from jobmatch.llm import OpenRouter, ProviderError, free_models

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="JobMatch UA",layout="wide")
st.title("JobMatch UA")
st.caption("Find Ukrainian-market IT roles using your CV, confirmed preferences and traceable evidence.")
if "jobs" not in st.session_state:
    st.session_state.jobs=load_jobs()
    st.session_state.source_label="Historical Djinni sample (2020–2023)"

# Rebuild records from data so hot reload cannot retain incompatible model classes.
def record_data(value):
    return value.model_dump() if hasattr(value,"model_dump") else value

st.session_state.jobs=[Job.model_validate(record_data(j)) for j in st.session_state.jobs]
if "profile" in st.session_state:
    st.session_state.profile=Profile.model_validate(record_data(st.session_state.profile))
if "result" in st.session_state:
    saved,diagnostics,prefs,source_hash,cv_hash=st.session_state.result
    st.session_state.result=([Recommendation.model_validate(record_data(r)) for r in saved],diagnostics,Preferences.model_validate(record_data(prefs)),source_hash,cv_hash)

with st.sidebar:
    st.header("Vacancy source")
    st.write(st.session_state.source_label)
    st.write(f"{len(st.session_state.jobs)} records")
    if st.button("Use historical dataset"):
        st.session_state.jobs=load_jobs();st.session_state.source_label="Historical Djinni sample (2020–2023)";st.rerun()
    if st.button("Use saved DOU snapshot"):
        saved=[Job.model_validate(row) for row in json.loads((ROOT/"data/dou_snapshot.json").read_text(encoding="utf-8"))]
        if saved:
            st.session_state.jobs=saved
            st.session_state.source_label="Saved DOU feed, retrieved "+saved[0].retrieved_at+"; availability not independently checked"
            st.rerun()
        else:st.warning("No saved feed entries available. Try a live fetch.")
    if st.button("Fetch current DOU RSS"):
        try:
            with st.spinner("Retrieving the public feed..."):
                fresh=fetch_dou()
            if not fresh:st.error("Feed returned no usable jobs. Existing source retained.")
            else:
                st.session_state.jobs=fresh;st.session_state.source_label="DOU RSS, retrieved now; availability not independently checked";st.rerun()
        except Exception as error:st.error(f"Live retrieval failed ({type(error).__name__}). Existing data retained and still labeled.")
    st.caption("Historical records are for reproducible experiments. A retrieved feed entry is not a guarantee that recruitment remains open.")
    if st.button("List free OpenRouter models"):
        try:st.dataframe(free_models())
        except Exception as error:st.error(f"Catalog unavailable: {type(error).__name__}")

example=(ROOT/"examples/data_profile.txt").read_text(encoding="utf-8") if (ROOT/"examples/data_profile.txt").exists() else "Data analyst. Python, SQL, Pandas. 2 years of experience. English B2."
with st.form("cv_input"):
    uploaded=st.file_uploader("Searchable PDF or UTF-8 TXT CV",type=["pdf","txt"],max_upload_size=5)
    pasted=st.text_area("Or paste your CV text",height=180)
    use_example=st.checkbox("Use the clearly labeled synthetic Data/AI example",value=False)
    mode=st.selectbox("CV analysis",["Local rule baseline — no external calls","OpenRouter — sends redacted CV text to the configured provider"])
    analyze=st.form_submit_button("Analyze CV")
if analyze:
    try:
        if use_example:text=redact_contacts(example)
        elif uploaded:text=parse_cv(uploaded.getvalue(),uploaded.name)
        else:text=parse_cv(pasted.encode("utf-8"),"cv.txt")
        with st.spinner("Extracting supported profile facts..."):
            stats={}
            if mode.startswith("Local"):
                profile=extract_local(text)
            else:
                adapter=OpenRouter()
                try:
                    profile=adapter.extract(text)
                    stats=adapter.validation_stats
                finally:adapter.client.close()
            validate_profile(profile,text)
        st.session_state.cv=text;st.session_state.profile=profile
        st.session_state.example=use_example
        st.session_state.validation_stats=stats
        st.session_state.pop("result",None)
    except (ValueError,ProviderError) as error:st.error(str(error))

if "profile" in st.session_state:
    profile=st.session_state.profile;cv=st.session_state.cv
    if st.session_state.get("example"):st.info("Synthetic demonstration CV. It is not your personal CV or an independent model evaluation.")
    st.subheader("Review the extracted profile")
    st.write("Analysis mode:",profile.mode)
    st.json(profile.model_dump())
    cleanup=st.session_state.get("validation_stats",{})
    if cleanup.get("skills_discarded") or cleanup.get("fields_cleared"):
        st.warning(f"Evidence review removed {cleanup.get('skills_discarded',0)} unsupported skill claims and cleared {cleanup.get('fields_cleared',0)} unsupported fields. Review the remaining profile before searching.")
    if cleanup.get("quotes_recovered"):
        st.caption(f"Matched {cleanup['quotes_recovered']} evidence quotes to the original CV using case/whitespace normalization; stored quotes preserve the original text.")
    if not profile.skills:st.warning("No skills were extracted. Review the CV and analysis mode before searching.")
    st.caption("Local experience extraction takes the largest explicit year count; per-skill or mixed contexts can be wrong. Unknowns and extraction mistakes should be reviewed before use.")
    with st.form("preferences"):
        st.write("Clarification: what role, location and work format should guide this search?")
        role=st.selectbox("Target direction",["Data Engineering","Data Analytics","AI/ML Engineer","Other"])
        st.caption("Direction guides ranking rather than enforcing an exact job-title category. Review adjacent roles and unknown conditions.")
        other=st.text_input("Role keywords if Other")
        city=st.text_input("City (leave blank for any)")
        remote=st.checkbox("Remote only")
        unknown=st.checkbox("Include jobs with unknown eligibility/requirements, visibly marked",value=True)
        reviewed=st.checkbox("I reviewed the extracted profile and confirm these search preferences")
        search=st.form_submit_button("Find matching vacancies")
    if search:
        if not reviewed:st.warning("Review the profile and confirm your preferences first.")
        else:
            prefs=Preferences(role=other if role=="Other" else role,city=city,remote_only=remote,include_unknown=unknown,confirmed=True)
            with st.spinner("Filtering and ranking source records..."):
                index=SearchIndex(st.session_state.jobs)
                results,diagnostics=index.rank(cv,profile,prefs,k=10)
            st.session_state.result=(results,diagnostics,prefs,hashlib.sha256(json.dumps([j.model_dump() for j in st.session_state.jobs],sort_keys=True).encode()).hexdigest(),hashlib.sha256(cv.encode()).hexdigest())
    if "result" in st.session_state:
        results,diagnostics,prefs,source_hash,cv_hash=st.session_state.result
        current_hash=hashlib.sha256(json.dumps([j.model_dump() for j in st.session_state.jobs],sort_keys=True).encode()).hexdigest()
        if current_hash!=source_hash or hashlib.sha256(cv.encode()).hexdigest()!=cv_hash:
            st.warning("CV or source changed. Run the search again; old results are not shown as current.")
        else:
            st.subheader("Ranked results")
            st.caption("Results reflect the last submitted preferences: "+str(prefs.model_dump()))
            st.write(f"Searched {diagnostics['searched']}; eligible ranked records: {diagnostics['eligible']}")
            if not results:st.info("No matching records under these filters. Review unknown-condition policy, CV facts, or source coverage.")
            for i,r in enumerate(results,1):
                if r.job.url:
                    st.markdown(f"**{i}. {r.job.title}**")
                    st.markdown(f"Vacancy URL: [{r.job.url}]({r.job.url})")
                with st.expander(f"{i}. {r.job.title} — {r.job.company}"):
                    st.write("Ranking score:",round(r.score,4),"(retrieval relevance; not a hiring probability)")
                    st.write("Source:",r.job.source,"Published:",r.job.published,"Retrieved:",r.job.retrieved_at)
                    if not r.job.url:st.info("Archived record without a source URL. Current availability is not established.")
                    st.write("Explicitly matched skills:",r.matched_skills)
                    st.write("Job-mentioned skills unmentioned in CV:",r.unmentioned_skills)
                    st.write("Unknown conditions:",r.unknowns)
                    st.json(r.evidence)
                    st.write(r.job.description)
            files=export_results(results,cv,profile,prefs,diagnostics)
            for name,content in files.items():st.download_button(f"Download {name}",content,name)
