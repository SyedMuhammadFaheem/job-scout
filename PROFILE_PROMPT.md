# Resume → profile.json prompt

Use this once during setup. Paste the prompt below into any LLM chat (Claude, ChatGPT, Gemini, and so on), attach or paste your resume, and save the two JSON blocks it returns as `profile.json` and `config.json`.

Check the output before you use it. The LLM only suggests values, and you know your job search better than it does.

---

```text
You are setting up a job-matching tool. Read my resume below and produce two JSON files.
Output ONLY two fenced json code blocks: first profile.json, then config.json. No commentary.

profile.json must match this schema exactly:
{
  "years_experience": <number, total professional years, excluding internships unless that's all there is>,
  "titles": [<job titles I have held or am clearly qualified for>],
  "skills": [<languages, frameworks, databases, core tools, using their common names, e.g. "React", "PostgreSQL">],
  "technologies": [<cloud services, platforms, and supporting tools>],
  "domains": [<industries I've worked in, lowercase>],
  "locations": [<my city, "Country", and "Remote" if I'd take remote work>],
  "work_modes": [<any of "remote", "hybrid", "onsite">],
  "education": [<degrees, short form, e.g. "BS Computer Science">],
  "certifications": [<named certifications only, no generic course platforms>],
  "keywords": [<5-10 short phrases that describe my specialty>],
  "exclude_keywords": [<title words for roles too senior or unrelated for me, e.g. "senior", "staff", "principal", "director">]
}

config.json must match this schema exactly:
{
  "target_titles": [<job titles I should search for>],
  "include_keywords": [<8-12 lowercase terms that should appear in a good job posting>],
  "exclude_keywords": [<same as profile.exclude_keywords>],
  "years_experience": <same as profile>,
  "locations": [<same as profile>],
  "work_modes": [<same as profile>],
  "sources": {
    "remoteok": {"enabled": true},
    "remotive": {"enabled": true},
    "arbeitnow": {"enabled": true},
    "jobicy": {"enabled": true},
    "weworkremotely": {"enabled": true, "categories": ["remote-full-time-programming"]},
    "himalayas": {"enabled": true},
    "hn_hiring": {"enabled": true},
    "greenhouse": {"enabled": true, "companies": []},
    "lever": {"enabled": true, "companies": []},
    "google_alerts": {"enabled": true, "feed_urls": []}
  },
  "matching": {
    "weights": {"title": 3, "skills": 2, "keywords": 1, "experience": 2, "location": 2, "recency": 1},
    "min_score": 4
  },
  "schedule": "09:00",
  "timezone": <IANA timezone for my location, e.g. "Asia/Karachi">,
  "email": {"to": <my email from the resume>},
  "max_daily_results": 30
}

Rules:
- Use only facts in the resume. Don't invent skills or experience.
- Keep skill names short and common, because matching is plain substring search on job text.
- If work mode or location preference isn't stated, use ["remote"] and my resume city plus "Remote".

My resume:
<paste resume here>
```
