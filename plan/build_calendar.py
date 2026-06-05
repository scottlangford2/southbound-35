"""
Generate the 156-week (three-year) content calendar for Southbound 35.

Run:
    python build_calendar.py > content-calendar.json

Each entry gets a `certainty` field so the reader can tell concrete
slots from placeholder slots:

    high   — title and approach already decided (next ~20 weeks)
    medium — series and position decided; specific title likely to
             shift (weeks 21-52)
    low    — series-paced placeholder; topic likely to be reassigned
             when real events (lege bills, court rulings, news) land
             (weeks 53-156)

The script encodes the pillar mix described in plan §3:
    ~60% pillar-2  corridor case studies
    ~15% pillar-1  public-finance mechanics
    ~10% pillar-3  econometric / statistical analysis
    ~10% pillar-4  program evaluation
    ~ 5% original analysis / framing / annual anchors

and the build order described in plan §5:
    pillar-2 follows concentric rings from San Marcos
    pillar-1 cycles through five mechanics series
    pillar-3 + pillar-4 interleave on roughly 8-12 week pacing
    annual anchors slot first
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta


def slugify(s: str) -> str:
    """URL-safe slug: lowercase, strip punctuation, collapse hyphens."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s[:60]

START = date(2026, 6, 8)   # Monday
N_WEEKS = 156              # three years


# ---------------------------------------------------------------------------
# Backlog content — explicit, ordered, editable
# ---------------------------------------------------------------------------

# Pillar 2: corridor case studies, in concentric-ring build order
CORRIDOR_BACKLOG = [
    # Ring 0 — Hays follow-ons (post titles drawn from next-series-outline.md)
    ("hays-county", "San Marcos and Texas State: an enrollment-finance feedback loop", "san-marcos-txst-feedback", 0),
    ("hays-county", "Kyle and Buda: the corridor's fastest-growing pair", "kyle-buda-paired", 0),
    ("hays-county", "Three districts, three school-finance worlds", "three-isd-comparison", 0),
    ("hays-county", "The western Hays Hill-Country edge", "western-hays-edge", 0),

    # Ring 1 — Comal (5)
    ("comal-county", "The Comal growth story", "comal-county-growth", 1),
    ("comal-county", "Comal projections, with the aquifer caveat", "comal-county-projections", 1),
    ("comal-county", "Comal water and the Edwards Aquifer Authority", "comal-county-water", 1),
    ("comal-county", "Comal schools and Comal ISD's bond posture", "comal-county-schools", 1),
    ("comal-county", "Who governs Comal County?", "comal-county-governance", 1),

    # Ring 1 — Caldwell (5)
    ("caldwell-county", "Caldwell County: the slow-growth neighbor", "caldwell-county-intro", 1),
    ("caldwell-county", "Lockhart and the I-35 east-side story", "caldwell-county-lockhart", 1),
    ("caldwell-county", "Plum Creek and Caldwell water", "caldwell-county-water", 1),
    ("caldwell-county", "Caldwell schools: Luling, Lockhart, Prairie Lea, McMahan", "caldwell-county-schools", 1),
    ("caldwell-county", "Who governs Caldwell County?", "caldwell-county-governance", 1),

    # Ring 1 — Guadalupe (5)
    ("guadalupe-county", "Guadalupe County: the Seguin–Schertz two-anchor pattern", "guadalupe-county-growth", 1),
    ("guadalupe-county", "Guadalupe projections and the Toyota supplier ecosystem", "guadalupe-county-projections", 1),
    ("guadalupe-county", "Guadalupe water: GBRA and the Carrizo–Wilcox", "guadalupe-county-water", 1),
    ("guadalupe-county", "Schertz–Cibolo–Universal City ISD: the three-county district", "guadalupe-county-schools", 1),
    ("guadalupe-county", "Who governs Guadalupe County?", "guadalupe-county-governance", 1),

    # Ring 1 — Southern Travis (4)
    ("southern-travis", "Dripping Springs and the SH 290 corridor", "southern-travis-dripping", 1),
    ("southern-travis", "Manchaca, Bee Cave, and the southwest Travis edge", "southern-travis-southwest", 1),
    ("southern-travis", "Southwest Travis schools: Eanes and Lake Travis ISDs", "southern-travis-schools", 1),
    ("southern-travis", "The Travis–Hays boundary as an institutional seam", "southern-travis-boundary", 1),

    # Ring 1 — Eastern Blanco (3)
    ("eastern-blanco", "Eastern Blanco: the Hill Country boundary with Hays", "eastern-blanco-intro", 1),
    ("eastern-blanco", "Pedernales Electric Cooperative as quasi-government", "eastern-blanco-pec", 1),
    ("eastern-blanco", "Blanco water: GCDs, private wells, and the Trinity Aquifer", "eastern-blanco-water", 1),

    # Ring 2 — Williamson (5)
    ("williamson-county", "Williamson growth: Round Rock, Cedar Park, and the Samsung shock", "williamson-county-growth", 2),
    ("williamson-county", "Williamson projections through 2050", "williamson-county-projections", 2),
    ("williamson-county", "Brushy Creek, Lake Georgetown, and the Samsung water question", "williamson-county-water", 2),
    ("williamson-county", "Williamson schools and the bond machine", "williamson-county-schools", 2),
    ("williamson-county", "Who governs Williamson County?", "williamson-county-governance", 2),

    # Ring 2 — Bexar Northside (5)
    ("bexar-northside", "The Bexar Northside: Stone Oak, 281, and the 1604 ring", "bexar-northside-intro", 2),
    ("bexar-northside", "Northside projections and the SAWS service area", "bexar-northside-projections", 2),
    ("bexar-northside", "SAWS, the Edwards, and the Vista Ridge pipeline", "bexar-northside-water", 2),
    ("bexar-northside", "NEISD vs NISD: two large suburban districts", "bexar-northside-schools", 2),
    ("bexar-northside", "Governance of an annexed exurban edge", "bexar-northside-governance", 2),

    # Ring 2 — Bastrop / eastern Caldwell (4)
    ("bastrop-edge", "Bastrop County: the eastern-corridor boom", "bastrop-edge-intro", 2),
    ("bastrop-edge", "Bastrop water and the Carrizo–Wilcox", "bastrop-edge-water", 2),
    ("bastrop-edge", "Bastrop and Smithville ISDs", "bastrop-edge-schools", 2),
    ("bastrop-edge", "Eastern Caldwell and the SH 130 development pattern", "bastrop-edge-sh130", 2),

    # Corridor framing & cross-cutting (interleaved, lower priority)
    ("i35-corridor", "Megaregion: the Austin–San Antonio corridor as one place", "megaregion-overview", None),
    ("i35-corridor", "I-35 freight: how the corridor moves things", "i35-freight", None),
    ("i35-corridor", "Commute sheds: who actually works where on I-35", "i35-commute-sheds", None),
    ("i35-corridor", "Lone Star Rail: a 15-year story of a project that didn't happen", "lone-star-rail-history", None),
    ("i35-corridor", "Edwards Aquifer politics across the corridor", "edwards-aquifer-corridor", None),
    ("i35-corridor", "The TXST Round Rock campus and its corridor effect", "txst-round-rock", None),
    ("i35-corridor", "Toyota San Antonio: a corridor anchor in its 20th year", "toyota-san-antonio-20", None),
    ("i35-corridor", "Samsung Taylor: a corridor anchor in its first year", "samsung-taylor-first-year", None),
]


# Pillar 1: public-finance mechanics, cycled in series order
PILLAR_1_BACKLOG = [
    # Property tax mechanics — the first two (property-tax-101, eanes-recapture)
    # are seeded as queued slots, so they are NOT in the iter backlog.
    ("property-tax-mechanics", "Truth-in-Taxation 101: reading the worksheets", "truth-in-taxation-101"),
    ("property-tax-mechanics", "Appraisal districts: how value is set", "appraisal-districts-101"),
    ("property-tax-mechanics", "Homestead exemptions and the 10% cap", "homestead-exemptions"),

    # Sales tax mechanics
    ("sales-tax-mechanics", "Sales tax 101: the second-biggest local revenue line", "sales-tax-101"),
    ("sales-tax-mechanics", "Type A and Type B EDCs: the mechanics", "type-ab-edc-mechanics"),
    ("sales-tax-mechanics", "MTA/ATD slices: how transit gets its penny", "mta-atd-slice"),
    ("sales-tax-mechanics", "Special Purpose Districts and sales tax", "spd-sales-tax"),

    # Special districts
    ("special-districts", "MUDs explained: the special-district mechanics", "muds-explained"),
    ("special-districts", "ESDs: the quiet revenue layer", "esds-explained"),
    ("special-districts", "Hospital districts and GCDs", "hospital-and-gcd-districts"),
    ("special-districts", "4,400 entities: the special-district census", "special-districts-overview"),

    # State aid formulas
    ("state-aid-formulas", "The Foundation School Program: how it actually works", "fsp-mechanics"),
    ("state-aid-formulas", "County road & bridge state aid", "county-road-bridge-aid"),
    ("state-aid-formulas", "Sales-tax holdbacks: state's diversion mechanics", "sales-tax-holdbacks"),
    ("state-aid-formulas", "Federal pass-through dollars in Texas budgets", "federal-pass-through"),

    # Bond mechanics
    ("bond-mechanics", "Voter-approval thresholds and bond elections", "bond-voter-approval"),
    ("bond-mechanics", "Debt service: how the I&S rate is set", "debt-service-mechanics"),
    ("bond-mechanics", "Taxable vs tax-exempt issuance", "taxable-vs-tax-exempt"),
    ("bond-mechanics", "What bond counsel opinions actually say", "bond-counsel-opinions"),
]


# Pillar 3: econometric / statistical analysis
PILLAR_3_BACKLOG = [
    "DID walkthrough using SB 2's cap as a quasi-treatment",
    "Regression discontinuity at the bond-approval threshold",
    "Synthetic control: a county after a major plant closure",
    "Replication of a published Texas-focused finding",
    "Spatial econometrics on corridor employment outcomes",
    "Bond-election turnout: what the Texas data show",
    "Power analysis for evaluation designs (using a TX program)",
    "How to read a coefficient table — a TX paper, line by line",
    "Event study: the February 2021 winter storm",
    "Fixed effects vs random effects with TX panel data",
    "Standard error clustering choices for county-level analysis",
    "Instrumental variables: what's plausibly exogenous in Texas",
    "Difference-in-differences with staggered adoption (HB 3)",
    "Heterogeneous treatment effects: who actually benefits?",
    "Pre-trend testing and the parallel-trends assumption",
    "Causal inference from observational TX program data",
]


# Pillar 4: program evaluation
PILLAR_4_BACKLOG = [
    "Type A/B EDCs: what the audits show",
    "HB 3 compression: what changed for school M&O",
    "SB 2 levy caps: did the 3.5% rate-growth ceiling bite?",
    "The Texas Enterprise Fund: 20 years of grants",
    "Tax Increment Reinvestment Zones in fast-growing TX cities",
    "Texas Enterprise Zone program: cumulative effects",
    "The Property Value Study and its school-finance role",
    "Regional water plan implementation: who delivered?",
    "Texas Hometown Heroes: housing subsidy take-up",
    "Local film incentives: do they pay back?",
    "Hotel Occupancy Tax: what cities actually spend it on",
    "Toyota San Antonio: 20-year incentive package retrospective",
    "Tesla Austin: three years in",
    "Samsung Taylor: one year in",
    "Chapter 313 incentives: what the post-mortem data show",
    "Texas Emerging Technology Fund: a closed-program autopsy",
]


# Annual anchors — fixed seasonal slots
def annual_anchors():
    """Slots that recur on a known cadence each year."""
    out = []
    for yr in (2026, 2027, 2028, 2029):
        # Year in review: last Monday of December
        d = date(yr, 12, 31)
        while d.weekday() != 0:
            d -= timedelta(days=1)
        out.append((d, "annual-anchor", f"Year in review: {yr}", f"year-in-review-{yr}", "framing"))

        # Bond election preview: second Monday of October
        d = date(yr, 10, 1)
        while d.weekday() != 0:
            d += timedelta(days=1)
        d += timedelta(days=7)
        out.append((d, "annual-anchor", f"Bond election preview: corridor edition ({yr})", f"bond-election-preview-{yr}", "original-analysis"))

        # Bond election post-mortem: second Monday of November
        d = date(yr, 11, 1)
        while d.weekday() != 0:
            d += timedelta(days=1)
        d += timedelta(days=7)
        out.append((d, "annual-anchor", f"Bond election results: corridor edition ({yr})", f"bond-election-results-{yr}", "original-analysis"))

        # Comptroller revenue estimate response: first Monday of February
        d = date(yr, 2, 1)
        while d.weekday() != 0:
            d += timedelta(days=1)
        out.append((d, "annual-anchor", f"Reading the {yr} Comptroller revenue estimate", f"comptroller-bre-{yr}", "public-finance"))

    # Legislative session structural posts (2027 odd year, Jan–May)
    leg_2027 = [
        ("Lege session preview: what's on the table for local finance", "lege-2027-preview"),
        ("Lege session: school finance bills filed",                    "lege-2027-school-finance"),
        ("Lege session: property tax bills filed",                      "lege-2027-property-tax"),
        ("Lege session: special-district reform",                       "lege-2027-special-districts"),
        ("Lege session post-mortem: what passed and what didn't",       "lege-2027-post-mortem"),
    ]
    for (topic, slug), month in zip(leg_2027, (1, 2, 3, 4, 5)):
        d = date(2027, month, 1)
        while d.weekday() != 0:
            d += timedelta(days=1)
        out.append((d, "annual-anchor", topic, slug, "public-finance"))

    # 2029 lege session (post-2026 election)
    leg_2029 = [
        ("Lege session 2029 preview",      "lege-2029-preview"),
        ("Lege session 2029 post-mortem",  "lege-2029-post-mortem"),
    ]
    for (topic, slug), month in zip(leg_2029, (2, 4)):
        d = date(2029, month, 1)
        while d.weekday() != 0:
            d += timedelta(days=1)
        out.append((d, "annual-anchor", topic, slug, "public-finance"))

    return out


# ---------------------------------------------------------------------------
# Calendar build
# ---------------------------------------------------------------------------

@dataclass
class Slot:
    date: str
    title: str
    slug: str
    pillar: str
    kind: str
    status: str
    certainty: str
    series: str | None = None
    ring: int | None = None
    notes: str = ""


def slot_pillar(week_idx: int) -> str:
    """Return the intended pillar for week `week_idx` under the rotation
    pattern. Roughly 60/15/10/10/5 over a 20-week window."""
    pattern = [
        "p2", "p2", "p1", "p2", "p3", "p2", "p4", "p2", "p2", "p1",
        "p2", "p3", "p2", "p2", "p1", "p2", "p4", "p2", "p2", "p1",
    ]
    return pattern[week_idx % len(pattern)]


def build_calendar() -> list[Slot]:
    mondays = [START + timedelta(weeks=i) for i in range(N_WEEKS)]
    slots: dict[date, Slot] = {}

    # 1) Place all annual anchors first; they take priority over the rotation.
    for anchor_date, _, title, slug, pillar in annual_anchors():
        if anchor_date < mondays[0] or anchor_date > mondays[-1]:
            continue
        slots[anchor_date] = Slot(
            date=anchor_date.isoformat(),
            title=title,
            slug=slug,
            pillar=pillar,
            kind="original-analysis" if "preview" in slug or "results" in slug else "explainer",
            status="planned",
            certainty="medium",
            notes="Annual anchor — fixed seasonal slot."
        )

    # 2) Seed the first three slots with the three queued posts under review.
    queued = [
        (date(2026, 6, 8), "How a Texas Property Tax Bill is Built", "property-tax-101",
         "public-finance", "explainer", "property-tax-mechanics",
         "PDF in ~/Dropbox/southbound-35-drafts/01_*.pdf"),
        (date(2026, 6, 15), "Eanes ISD and Robin Hood: How Recapture Actually Works", "eanes-recapture",
         "public-finance", "explainer", "property-tax-mechanics",
         "PDF in ~/Dropbox/southbound-35-drafts/02_*.pdf"),
        (date(2026, 6, 22), "Eighty Miles: A Short History of the I-35 Corridor",
         "i35-austin-sa", "economic-development", "case-study", "i35-corridor",
         "PDF in ~/Dropbox/southbound-35-drafts/03_*.pdf"),
    ]
    for d, title, slug, pillar, kind, series, note in queued:
        slots[d] = Slot(
            date=d.isoformat(), title=title, slug=slug, pillar=pillar,
            kind=kind, status="review", certainty="high",
            series=series, notes=note
        )

    # 3) Pillar-2 queue (corridor) — fill p2 slots in order.
    p2_iter = iter(CORRIDOR_BACKLOG)
    p1_iter = iter(PILLAR_1_BACKLOG)
    p3_iter = iter(PILLAR_3_BACKLOG)
    p4_iter = iter(PILLAR_4_BACKLOG)

    def pop_next(it, fallback_pillar):
        try:
            return next(it)
        except StopIteration:
            return None

    for i, d in enumerate(mondays):
        if d in slots:
            continue
        target = slot_pillar(i)
        certainty = "high" if i < 20 else ("medium" if i < 52 else "low")
        status = "planned" if i < 52 else "backlog"

        if target == "p2":
            entry = pop_next(p2_iter, None)
            if entry:
                series, title, slug, ring = entry
                pillar = "economic-development"
                slots[d] = Slot(
                    date=d.isoformat(), title=title, slug=slug, pillar=pillar,
                    kind="case-study", status=status, certainty=certainty,
                    series=series, ring=ring,
                    notes=("Corridor build, Ring " + str(ring)) if ring is not None else "Corridor framing"
                )
                continue
        if target == "p1":
            entry = pop_next(p1_iter, None)
            if entry:
                series, title, slug = entry
                slots[d] = Slot(
                    date=d.isoformat(), title=title, slug=slug,
                    pillar="public-finance", kind="explainer",
                    status=status, certainty=certainty, series=series,
                    notes="Pillar-1 mechanics."
                )
                continue
        if target == "p3":
            topic = pop_next(p3_iter, None)
            if topic:
                slug = slugify(topic)
                slots[d] = Slot(
                    date=d.isoformat(), title=topic, slug=slug,
                    pillar="econometric-analysis", kind="original-analysis",
                    status=status, certainty=certainty,
                    notes="Pillar-3 stats / methods."
                )
                continue
        if target == "p4":
            topic = pop_next(p4_iter, None)
            if topic:
                slug = slugify(topic)
                slots[d] = Slot(
                    date=d.isoformat(), title=topic, slug=slug,
                    pillar="program-evaluation", kind="evaluation",
                    status=status, certainty=certainty,
                    notes="Pillar-4 evaluation."
                )
                continue

        # Fallback — if the target pillar's backlog is exhausted, pull
        # from the longest remaining backlog.
        for it_name, it, pillar, kind in [
            ("p2", p2_iter, "economic-development", "case-study"),
            ("p1", p1_iter, "public-finance", "explainer"),
            ("p4", p4_iter, "program-evaluation", "evaluation"),
            ("p3", p3_iter, "econometric-analysis", "original-analysis"),
        ]:
            entry = pop_next(it, None)
            if entry:
                if it_name == "p2":
                    series, title, slug, ring = entry
                    slots[d] = Slot(
                        date=d.isoformat(), title=title, slug=slug,
                        pillar=pillar, kind=kind, status=status,
                        certainty=certainty, series=series, ring=ring,
                        notes=f"Filler from {it_name} backlog"
                    )
                elif it_name == "p1":
                    series, title, slug = entry
                    slots[d] = Slot(
                        date=d.isoformat(), title=title, slug=slug,
                        pillar=pillar, kind=kind, status=status,
                        certainty=certainty, series=series,
                        notes=f"Filler from {it_name} backlog"
                    )
                else:
                    title = entry
                    slug = slugify(title)
                    slots[d] = Slot(
                        date=d.isoformat(), title=title, slug=slug,
                        pillar=pillar, kind=kind, status=status,
                        certainty=certainty,
                        notes=f"Filler from {it_name} backlog"
                    )
                break
        else:
            # No backlog left — leave an unassigned placeholder
            slots[d] = Slot(
                date=d.isoformat(),
                title="UNASSIGNED — populate from backlog",
                slug=f"unassigned-{d.isoformat()}",
                pillar="tbd", kind="tbd", status="backlog",
                certainty="low",
                notes="All pillar backlogs exhausted at this point — add new topics."
            )

    return [slots[d] for d in mondays]


def main() -> None:
    cal = build_calendar()

    # Summary counts
    by_pillar: dict[str, int] = {}
    by_certainty: dict[str, int] = {}
    for s in cal:
        by_pillar[s.pillar] = by_pillar.get(s.pillar, 0) + 1
        by_certainty[s.certainty] = by_certainty.get(s.certainty, 0) + 1

    output = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "_comment": ("Content calendar for Southbound 35, generated by "
                     "build_calendar.py. Re-run to regenerate after editing "
                     "the backlogs in the script."),
        "last_updated": "2026-06-05",
        "review_rule": "No post goes live without Scott's review of the PDF.",
        "scope": ("Four pillars only: public-finance, economic-development, "
                  "econometric-analysis, program-evaluation."),
        "horizon_weeks": N_WEEKS,
        "certainty_levels": {
            "high":   "Title and approach already decided (next ~20 weeks)",
            "medium": "Series and position decided; specific title likely to shift (weeks 21-52)",
            "low":    "Series-paced placeholder; topic likely reassigned when real events land (weeks 53+)",
        },
        "summary_by_pillar": by_pillar,
        "summary_by_certainty": by_certainty,
        "calendar": [asdict(s) for s in cal],
    }

    # Drop null fields so the JSON stays readable
    for entry in output["calendar"]:
        for key in list(entry.keys()):
            if entry[key] is None:
                del entry[key]

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
