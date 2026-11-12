import re
import os
import sys

# Paths
WEB_ROOT = '/Users/sb/Documents/garbage/personal_website'
LINEAGE_ROOT = '/Users/sb/Documents/garbage/systems-innovation-lineage'

with open(f'{WEB_ROOT}/src/data/articles.ts') as f:
    art_content = f.read()
    articles_map = dict(re.findall(r'\{\s*slug:\s*[\'\"]([^\'\"]+)[\'\"],.*?title:\s*[\'\"]([^\'\"]+)[\'\"]', art_content, re.DOTALL))

with open(f'{WEB_ROOT}/src/data/caseStudies.ts') as f:
    cs_content = f.read()
    case_studies_map = dict(re.findall(r'\{\s*slug:\s*[\'\"]([^\'\"]+)[\'\"],.*?title:\s*[\'\"]([^\'\"]+)[\'\"]', cs_content, re.DOTALL))

with open(f'{WEB_ROOT}/src/data/dueDiligenceReports.ts') as f:
    rep_content = f.read()
    reports_map = dict(re.findall(r'\{\s*slug:\s*[\'\"]([^\'\"]+)[\'\"],.*?title:\s*[\'\"]([^\'\"]+)[\'\"]', rep_content, re.DOTALL))

# Import DATA from /tmp/enrich_lineage.py
sys.path.insert(0, '/tmp')
from enrich_lineage import DATA

# Read innovators from innovators.ts
with open(f'{WEB_ROOT}/src/data/innovators.ts') as f:
    inn_text = f.read()

# Extract innovator blocks
blocks = re.findall(r'\{\s*id:\s*(\d+),\s*slug:\s*[\'\"]([^\'\"]+)[\'\"],.*?name:\s*[\'\"]([^\'\"]+)[\'\"],.*?category:\s*[\'\"]([^\'\"]+)[\'\"],.*?historicalPeriod:\s*[\'\"]([^\'\"]+)[\'\"],.*?approximateDate:\s*[\'\"]([^\'\"]+)[\'\"],.*?geographicalAssociation:\s*[\'\"]([^\'\"]+)[\'\"],.*?keyInvention:\s*[\'\"]([^\'\"]+)[\'\"],.*?worldChangingImpact:\s*[\'\"]([^\'\"]+)[\'\"],.*?attributionNote:\s*[\'\"]([^\'\"]+)[\'\"],.*?systemicLesson:\s*[\'\"]([^\'\"]+)[\'\"],.*?breakthroughAnalysis:\s*\[(.*?)\]\s*,\s*modernArchitectureRelevance:\s*\'(.*?)\',.*?sameAs:\s*\[(.*?)\]', inn_text, re.DOTALL)

print(f"Parsed {len(blocks)} innovator blocks from innovators.ts")

os.makedirs(f'{LINEAGE_ROOT}/profiles', exist_ok=True)
os.makedirs(f'{LINEAGE_ROOT}/scripts', exist_ok=True)

table_rows = []

for block in blocks:
    i_id, slug, name, category, period, date, geo, invention, impact, attribution, lesson, breakthrough_raw, modern_rel_raw, sameas_raw = block
    
    # Parse paragraphs
    paragraphs = re.findall(r'[\'\"]([^\'\"]+)[\'\"]', breakthrough_raw)
    same_as_urls = re.findall(r'[\'\"]([^\'\"]+)[\'\"]', sameas_raw)
    
    enrich = DATA.get(slug, {})
    rel_articles = enrich.get('relatedArticleSlugs', [])
    rel_cases = enrich.get('relatedCaseStudySlugs', [])
    rel_reps = enrich.get('relatedReportSlugs', [])
    tool_url = enrich.get('relatedToolUrl', '')
    tool_label = enrich.get('relatedToolLabel', '')
    
    # Modern relevance: convert internal relative links (/articles/...) to absolute https://shashwat.si/...
    modern_rel_md = enrich.get('modernRelevance', modern_rel_raw)
    modern_rel_md = re.sub(r'\]\(/', r'](https://shashwat.si/', modern_rel_md)
    
    # Breakthrough paragraphs: also convert any relative links to absolute
    paragraphs_md = [re.sub(r'\]\(/', r'](https://shashwat.si/', p) for p in paragraphs]
    
    # Build markdown profile with *** instead of triple hyphens
    md = f"""# {name} ({date})

> **Canonical Web Profile:** [https://shashwat.si/innovators/{slug}/](https://shashwat.si/innovators/{slug}/)  
> **Historical Category:** {category}  
> **Geographic Association:** {geo}  
> **Key Invention:** {invention}

***

## Core Systems Takeaway

> "{lesson}"

**World-Changing Impact:** {impact}

***

## The Architectural Breakthrough

"""
    for p in paragraphs_md:
        md += f"{p}\n\n"

    md += f"""***

## Modern Systems Relevance & Practitioner Commentary

*Architectural analysis by [Dr. Shashwat Bishwen](https://shashwat.si):*

{modern_rel_md}

***

## Connected Engineering Work & Technical Backlinks

This historical innovation provides the foundational lineage for several published technical investigations, production case studies, diagnostic tools, and diligence reports by Dr. Shashwat Bishwen:

### In-Depth Technical Articles
"""
    for a in rel_articles:
        title = articles_map.get(a, a)
        md += f"- [{title}](https://shashwat.si/articles/{a}/)\n"

    md += "\n### Production Case Studies\n"
    for c in rel_cases:
        title = case_studies_map.get(c, c)
        md += f"- [{title}](https://shashwat.si/case-studies/{c}/)\n"

    md += "\n### Executive Technical Due Diligence Reports\n"
    for r in rel_reps:
        title = reports_map.get(r, r)
        md += f"- [{title}](https://shashwat.si/due-diligence-reports/{r}/)\n"

    if tool_url:
        md += f"\n### Live Diagnostic Engine & Simulator\n- [{tool_label}](https://shashwat.si{tool_url})\n"

    md += f"""
***

## Attribution & Historical Context

{attribution}

### Reference Authorities
"""
    for url in same_as_urls:
        md += f"- [{url}]({url})\n"

    md += f"""
***

*Curated by [Dr. Shashwat Bishwen](https://shashwat.si) (Solution Assembler & Chief Systems Architect, TEDx). For executive advisory, technical due diligence, and platform triage, visit [shashwat.si](https://shashwat.si).*
"""

    # Check constraints
    assert '\u2014' not in md, f"Em dash in profile: {slug}"
    assert ('-' * 2) not in md, f"Double hyphen in profile: {slug}"
    assert 'TEDx speaker' not in md, f"Forbidden phrase in profile: {slug}"

    with open(f'{LINEAGE_ROOT}/profiles/{slug}.md', 'w') as pf:
        pf.write(md)

    # Collect table row
    first_art = f"[{articles_map.get(rel_articles[0], 'Technical Article')}](https://shashwat.si/articles/{rel_articles[0]}/)" if rel_articles else ""
    first_cs = f"[{case_studies_map.get(rel_cases[0], 'Case Study')}](https://shashwat.si/case-studies/{rel_cases[0]}/)" if rel_cases else ""
    table_rows.append(f"| [{name}](https://shashwat.si/innovators/{slug}/) | {category} | {date} | {invention} | {first_art} <br> {first_cs} |")

print("All 32 profile markdown files generated and validated!")

# Generate README.md
readme = f"""# Systems Innovation Lineage

A curated, open-source architectural lineage tracing foundational breakthroughs across 2,000+ years of computing, distributed systems, information theory, medicine, and industrial engineering to modern production software systems.

Curated by **[Dr. Shashwat Bishwen](https://shashwat.si)** (Solution Assembler & Chief Systems Architect, TEDx).

***

## About This Knowledge Base

Modern software engineering often treats distributed systems design, site reliability engineering, telemetry pipeline design, and algorithmic optimization as recent phenomena. In reality, modern cloud architectures rest upon physical, mathematical, and systemic principles established across centuries:

- **State machine bounds and halting undecidability:** [Alan Turing](https://shashwat.si/innovators/alan-turing/) (1936) &rarr; modern timeouts, circuit breakers, and [distributed transaction coordination](https://shashwat.si/case-studies/zero-downtime-database-topology-migration/).
- **Decoupled compute and storage:** [Charles Babbage](https://shashwat.si/innovators/charles-babbage/) (1837) &rarr; database read replicas, sharded storage engines, and [managing technical debt](https://shashwat.si/articles/unit-economics-of-technical-debt/).
- **Information entropy and signal-to-noise ratio:** [Claude Shannon](https://shashwat.si/innovators/claude-shannon/) (1948) &rarr; telemetry log sampling, APM cardinality limits, and [combating the observability tax](https://shashwat.si/articles/observability-tax-forensic-audit-how-your-unified-platform-bishwen-eijmc/).
- **Decentralized survivable mesh routing:** [Paul Baran](https://shashwat.si/innovators/paul-baran/) (1964) & [Radia Perlman](https://shashwat.si/innovators/radia-perlman/) (1985) &rarr; Spanning Tree Protocol, zero-trust overlay networks, and [eliminating single points of failure](https://shashwat.si/case-studies/eliminating-a-single-point-of-failure/).
- **Standardized clinical protocols and operational velocity:** [Sushruta](https://shashwat.si/innovators/sushruta/) (c. 600 BCE), [Charaka](https://shashwat.si/innovators/charaka/) (c. 100 BCE), and [Florence Nightingale](https://shashwat.si/innovators/florence-nightingale/) (1854) &rarr; operational telemetry, ward discharge latency reduction, and [BedTurn hospital velocity simulation](https://shashwat.si/tools/bedturn/).

***

## Innovator Syllabus & Connected Technical Research

| Innovator | Domain | Historical Era | Key Architectural Contribution | Connected Production Research (shashwat.si) |
| - | - | - | - | - |
"""

readme += "\n".join(table_rows)

readme += """

***

## Canonical Web Portal

The interactive web portal featuring client-side multi-filtering, search, verified historical portraits, and full responsive design is hosted on:

&rarr; **[https://shashwat.si/innovators/](https://shashwat.si/innovators/)**

***

## Repository Structure

```text
systems-innovation-lineage/
├── README.md               # Syllabus, lineage mapping, and connected research
├── scripts/
│   └── sync_lineage.py     # Two-way synchronization script with personal_website
└── profiles/               # 32 in-depth architectural profiles with live backlinks
    ├── ada-lovelace.md
    ├── alan-turing.md
    ├── apj-abdul-kalam.md
    ├── charles-babbage.md
    ├── claude-shannon.md
    └── ... (32 profiles)
```

***

## Synchronizing with shashwat.si

To keep the open-source profiles synchronized with the production website data:

```bash
python3 scripts/sync_lineage.py
```

This verifies that all canonical links, technical cross-links, case study references, and author credentials remain in sync across both repositories.

***

## Author & Curator

**Dr. Shashwat Bishwen**  
Solution Assembler & Chief Systems Architect, TEDx, and Author.  
Web: [https://shashwat.si](https://shashwat.si)  
Executive Advisory: [Fractional CTO Advisory](https://shashwat.si/fractional-cto-advisory/) | [Platform Stabilization](https://shashwat.si/platform-stabilization-triage/) | [Technical Due Diligence](https://shashwat.si/technical-due-diligence/)
"""

# Check constraints on README
assert '\u2014' not in readme, "Em dash in README"
assert '--' not in readme, "Double hyphen in README"
assert 'TEDx speaker' not in readme, "Forbidden phrase in README"

with open(f'{LINEAGE_ROOT}/README.md', 'w') as rf:
    rf.write(readme)

print("README.md generated and validated!")
