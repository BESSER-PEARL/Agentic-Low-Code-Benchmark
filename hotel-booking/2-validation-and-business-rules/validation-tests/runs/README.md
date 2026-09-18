# Recorded runs

Every number this benchmark reports comes from a run stored here. Each
directory holds the raw `behave` output for all three feature folders and a
`manifest.json` saying what was measured, against what, and when.

Nothing in a manifest is typed in by hand — the totals are parsed from the log
files sitting beside them, so a reader can check any figure by opening the log
and counting. If the two ever disagree, the log is right.

```
runs/
  <date>-<label>/
    manifest.json          what was run, against which versions, and the totals
    basic_functionality.txt  raw behave output
    constraints.txt
    behavior.txt
```

## What a manifest records

- **approach / tool / llm** — the columns a comparison table needs: whether the
  application was built purely from models, with an LLM, or a mix, and by what.
- **under_test** — the version of the tool that produced the application, and
  the addresses the suite drove. The version is stated by whoever records the
  run, not detected: the package installed beside the test suite is not the
  one that built the application, and reading it would quietly report the
  wrong number.
- **benchmark** — the commit of this repository, when `model.json` last changed,
  and whether the working tree was dirty. A dirty tree means the run cannot be
  reproduced exactly from the commit, so treat its numbers as provisional.
- **results** — per feature folder: passed, failed, skipped, duration, the names
  of the failing scenarios, and the log file to read.
- **totals** — the sums. These are what belongs in a comparison table.

## Reproducing a run

Start the application under test on the addresses the suite expects, then:

```bash
python record_run.py --label <version-or-tool> --tool "<what built it>" \
    --approach "Pure low-code" --llm "No LLM" --notes "<how it was generated>"
```

`BENCH_API` and `BENCH_UI` override the defaults (`http://localhost:8000` and
`http://localhost:3000`). The suite drives the generated interface with a real
browser, so a full run takes several minutes; that is the point, since it
exercises the application a user would actually get.

Start from an empty database. Several scenarios say "the database is empty" in
their background and assert on counts.

## Reading a failure honestly

A failing scenario is not automatically a defect. Three things look the same in
a log and mean different things:

- the tool built the feature and it misbehaves — a **correctness** problem;
- the tool cannot express the feature at all — a **completeness** problem;
- the scenario asserts something the requirements do not actually say — a
  problem with this suite, and worth a pull request.

The manifest does not classify failures, because that judgement needs the
source. Anyone comparing tools should make the call explicitly and say which
they counted.
