# EEE Opportunity Tracker

A small command-line tool that automatically checks hackathon/opportunity
RSS feeds, uses the Groq API (free, fast inference on open models like
Llama 3.3) to judge how relevant each posting is to an Electrical/Electronics
Engineering (EEE) student, and writes a clean Markdown digest of the best
matches.

## Why I built this

Finding hackathons, internships, and scholarships that are actually worth
an EEE student's time means manually checking several sites every week
and reading through postings that mostly aren't relevant. This tool
automates that: it pulls new postings from a list of feeds, asks an AI
model to score each one against my interests, and only surfaces the ones
worth a second look — as a dated report I can skim in under a minute.

## How it works

```
main.py
 ├─ fetch_opportunities.py   fetches & dedupes entries from RSS/Atom feeds
 ├─ ai_evaluator.py          asks Groq (Llama 3.3) to score each entry's relevance
 ├─ report_writer.py         writes the scored results to reports/YYYY-MM-DD.md
 └─ config.py                loads API key + feed/keyword settings
```

Each run:
1. Reads the feed URLs and interest keywords from `sources.json`
2. Fetches each feed and skips postings already seen in a previous run
   (tracked in `seen_entries.json`)
3. Sends each new posting to Groq with a short prompt asking whether
   it's relevant to an EEE student, plus a 0–10 score and one-line reason
4. Writes everything that clears the score threshold into a Markdown
   report, sorted best-match first

## Setup

```bash
git clone <this-repo-url>
cd eee-opportunity-tracker
pip install -r requirements.txt
cp .env.example .env        # then add your free Groq API key
cp sources.example.json sources.json   # then edit feed URLs/keywords
```

Get a free Groq API key (no credit card required) at
https://console.groq.com/keys.

## Usage

```bash
python main.py
```

This prints progress to the console and writes a report to
`reports/<today's date>.md`.

To run it automatically, schedule it with cron (Linux/macOS) or Task
Scheduler (Windows), e.g. daily at 8am:

```
0 8 * * * cd /path/to/eee-opportunity-tracker && python main.py
```

## Running tests

```bash
pytest tests/ -v
```

The tests cover the dedupe logic, AI-response parsing, and report
generation — the parts of the pipeline that don't require a live network
call or a real API key.

## What I learned building this

- How to build a small pipeline app as independent, testable modules
  instead of one long script (fetch → evaluate → report)
- Working with RSS/Atom feeds via `feedparser` and handling malformed or
  unreachable feeds gracefully instead of crashing the whole run
- Calling a generative AI API (Groq, OpenAI-compatible) directly over
  REST, including handling cases where the model doesn't return clean JSON
- Writing unit tests for logic that depends on external services, by
  isolating the parts that don't need the network (parsing, dedupe,
  formatting) and testing those directly
