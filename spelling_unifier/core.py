"""US/UK variant dictionary plus pattern rules (-ise/-ize, -our/-or, -yse/-yze, -tre/-ter)."""
import re
from collections import Counter

# Explicit pairs: UK -> US. Pattern rules below cover regular families.
VARIANTS = {
    "colour": "color", "behaviour": "behavior", "favour": "favor", "honour": "honor", "labour": "labor",
    "neighbour": "neighbor", "rumour": "rumor", "tumour": "tumor", "vapour": "vapor", "humour": "humor",
    "centre": "center", "fibre": "fiber", "litre": "liter", "metre": "meter", "theatre": "theater",
    "analyse": "analyze", "catalyse": "catalyze", "paralyse": "paralyze", "dialyse": "dialyze",
    "modelling": "modeling", "modelled": "modeled", "labelling": "labeling", "labelled": "labeled",
    "travelling": "traveling", "travelled": "traveled", "signalling": "signaling", "signalled": "signaled",
    "cancelled": "canceled", "cancelling": "canceling", "fuelled": "fueled", "channelled": "channeled",
    "tunnelling": "tunneling", "levelled": "leveled", "counselling": "counseling",
    "defence": "defense", "licence": "license", "offence": "offense", "pretence": "pretense",
    "grey": "gray", "programme": "program", "catalogue": "catalog", "dialogue": "dialog", "analogue": "analog",
    "oestrogen": "estrogen", "haemoglobin": "hemoglobin", "anaemia": "anemia", "anaesthesia": "anesthesia",
    "haematology": "hematology", "paediatric": "pediatric", "orthopaedic": "orthopedic", "foetus": "fetus",
    "oedema": "edema", "diarrhoea": "diarrhea", "leukaemia": "leukemia", "aluminium": "aluminum",
    "sulphur": "sulfur", "sulphate": "sulfate", "mould": "mold", "plough": "plow", "tyre": "tire",
    "ageing": "aging", "acknowledgement": "acknowledgment", "judgement": "judgment", "enrolment": "enrollment",
    "fulfil": "fulfill", "skilful": "skillful", "whilst": "while", "amongst": "among", "artefact": "artifact",
    "sceptical": "skeptical", "manoeuvre": "maneuver", "practise": "practice", "towards": "toward",
}
# Words ending in -ise that are spelled -ise in US English too.
ISE_EXCEPTIONS = {"advertise", "advise", "arise", "chastise", "circumcise", "comprise", "compromise", "concise",
                  "demise", "despise", "devise", "disguise", "enterprise", "excise", "exercise", "expertise",
                  "franchise", "improvise", "incise", "merchandise", "noise", "otherwise", "paradise", "poise",
                  "precise", "premise", "promise", "raise", "revise", "rise", "supervise", "surmise", "surprise",
                  "televise", "treatise", "wise", "likewise", "clockwise", "praise", "cruise", "bruise", "anise",
                  "guise", "reprise", "concise", "baptise"}
_ISE = re.compile(r"\b([A-Za-z]{2,}?)is(e|es|ed|ing|ation|ations|er|ers)\b")
_IZE = re.compile(r"\b([A-Za-z]{2,}?)iz(e|es|ed|ing|ation|ations|er|ers)\b")


def _case_like(src, word):
    if src.isupper():
        return word.upper()
    if src[0].isupper():
        return word[0].upper() + word[1:]
    return word


def _families():
    """Expand explicit variants with simple inflections (s, d, ing, ed, al)."""
    pairs = {}
    for uk, us in VARIANTS.items():
        pairs[uk] = us
        for suf in ("s", "ed", "ing", "al", "ally", "ful"):
            if uk.endswith("e") and suf in ("ed", "ing"):
                pairs[uk[:-1] + suf] = us[:-1] + suf if us.endswith("e") else us + suf
            elif not uk.endswith(("e", "ll")) or suf == "s":
                pairs[uk + suf] = us + suf
    return pairs


PAIRS = _families()
US_TO_UK = {v: k for k, v in PAIRS.items()}


def find_variants(text):
    """Return list of (offset, word, style, counterpart) for every spelling with a known variant."""
    hits = []
    for m in re.finditer(r"\b[A-Za-z]+\b", text):
        w, lw = m.group(0), m.group(0).lower()
        if lw in PAIRS:
            hits.append((m.start(), w, "uk", _case_like(w, PAIRS[lw])))
        elif lw in US_TO_UK and US_TO_UK[lw] != lw:
            hits.append((m.start(), w, "us", _case_like(w, US_TO_UK[lw])))
    for rx, style, repl in ((_ISE, "uk-ise", "iz"), (_IZE, "us-ize", "is")):
        for m in rx.finditer(text):
            base = (m.group(1) + "ise").lower()
            if base in ISE_EXCEPTIONS or m.group(1).lower().endswith(("w", "c")) or len(m.group(1)) < 3:
                continue
            if m.group(0).lower() in PAIRS or m.group(0).lower() in US_TO_UK:
                continue
            hits.append((m.start(), m.group(0), style, m.group(1) + repl + m.group(2)))
    return sorted(hits)


def dominant_style(hits):
    """Count spellings: returns (counts, majority) where majority is 'uk', 'us' or 'oxford' (UK with -ize)."""
    c = Counter()
    for _, _, style, _ in hits:
        c[style] += 1
    base = "uk" if c["uk"] >= c["us"] else "us"
    if base == "uk" and c["us-ize"] > c["uk-ise"]:
        return c, "oxford"
    if base == "us" and c["uk-ise"] > c["us-ize"]:
        return c, "us"
    if base == "uk":
        return c, "uk"
    return c, "us"


def unify(text, target):
    """Rewrite text to target style: 'us', 'uk' (-ise) or 'oxford' (UK spelling with -ize).

    Returns (new_text, changes) where changes is a Counter of 'old -> new'.
    """
    if target not in ("us", "uk", "oxford"):
        raise ValueError("target must be us, uk or oxford")
    changes = Counter()
    out, last = [], 0
    for pos, word, style, other in find_variants(text):
        flip = ((target == "us" and style in ("uk", "uk-ise")) or
                (target == "uk" and style in ("us", "us-ize")) or
                (target == "oxford" and style in ("us", "uk-ise")))
        if not flip or pos < last:
            continue
        out.append(text[last:pos])
        out.append(other)
        changes["%s -> %s" % (word, other)] += 1
        last = pos + len(word)
    out.append(text[last:])
    return "".join(out), changes
