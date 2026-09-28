from src.dedupe import dedupe_jobs, fingerprint


def make_job(source, title="Backend Engineer", company="Acme", location="Remote"):
    return {
        "title": title, "company": company, "location": location, "remote": True,
        "source": source, "application_url": f"https://{source}.com/job/1",
        "original_url": f"https://{source}.com/job/1",
    }


def test_fingerprint_stable_across_case_and_whitespace():
    a = fingerprint(make_job("s1", title="Backend  Engineer"))
    b = fingerprint(make_job("s2", title="backend engineer"))
    assert a == b


def test_dedupe_merges_same_job_across_sources():
    jobs = [make_job("remoteok"), make_job("remotive")]
    merged = dedupe_jobs(jobs)
    assert len(merged) == 1
    assert len(merged[0]["sources"]) == 2
    assert {s["source"] for s in merged[0]["sources"]} == {"remoteok", "remotive"}


def test_dedupe_keeps_distinct_jobs_separate():
    jobs = [make_job("remoteok", title="Backend Engineer"), make_job("remoteok", title="Frontend Engineer")]
    merged = dedupe_jobs(jobs)
    assert len(merged) == 2
