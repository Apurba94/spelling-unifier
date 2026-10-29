# spelling-unifier

**Detect mixed British/American spelling (`colour`/`color`, `analysed`/`analyzed`,
`-ise`/`-ize`) in a manuscript and rewrite it consistently to US, UK or Oxford spelling.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

International author teams produce manuscripts where Methods are British and Results American.
Journals require one variety, and spell checkers set to one locale flag the *other* spelling as a
"typo" without helping you choose. This tool counts both, reports the minority spellings with line
numbers, and fixes them in one pass.

## Features

- ~100 explicit UK/US pairs with inflections (colour, centre, analyse, modelling, haemoglobin,
  oestrogen, sulphur, programme, ageing, judgement ...)
- Pattern rules for `-ise`/`-ize` families with a list of words that are `-ise` in both
  (advise, revise, exercise, surprise ...)
- Three targets: `us`, `uk` (-ise) and `oxford` (British spelling with -ize, used by many UK journals)
- `--to auto` adopts the majority style; preserves capitalization; reports every change

## Usage

```bash
pip install .
spelling-unifier manuscript.tex                 # report minority spellings (exit 1 if any)
spelling-unifier manuscript.tex --to us -o manuscript_us.tex
spelling-unifier paper.md --to auto --in-place
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
