# Prior art, checked against current documentation

**Checked on 2026-09-20.** Every row below was verified against a page fetched on that date, with
the URL recorded. Nothing here is from memory or from a search snippet alone; where a page could
not be fetched and only a cached snippet was available, the row says so and is marked
lower-confidence. `02-SPEC.md` §12 lists "a comparison to ValidMind or deepchecks not verified
against their documentation on a stated date" as a reject, and this file is the record that
discharges it.

`01-BRIEF.md` §3 is the source of the claims being checked. Three of its claims are **wrong or
materially stale as of today** and are not carried into `README.md`:

1. **"ValidMind … is closed and enterprise"** — wrong as stated. ValidMind publishes a genuinely
   open-source client library.
2. **"automates SR 11-7 documentation and testing"** — stale. ValidMind's current pages cite
   **SR 26-2**, not SR 11-7.
3. **deepchecks "open source … runs component-level checks"** — true, but the brief omits that
   the company was **acquired by Check Point in May 2026** and the OSS project has shipped no
   release since December 2024.

There is also a fourth finding that is not about either vendor but governs the whole README:
**SR 11-7 was superseded on 2026-04-17 by SR 26-2.** This project already knew (`DECISIONS.md`
D-055, 2026-09-07) and the corpus holds both letters; the point is repeated here because a
prior-art check that did not notice it would be worthless.

---

## 0. The regulatory baseline — SR 11-7 is superseded

| claim | verdict |
|---|---|
| SR 11-7 is the current Federal Reserve model-risk guidance | **WRONG as of 2026-04-17** |

**What the documentation says.** The Federal Reserve's SR 26-2, *"Revised Guidance on Model Risk
Management"*, is dated **April 17, 2026**. Its "Supersedes" field lists *"SR letter 11-7, 'Guidance
on Model Risk Management' (April 4, 2011)"*. It is an interagency letter: the page opens *"The
Board of Governors of the Federal Reserve System, Office of the Comptroller of the Currency (OCC),
and Federal Deposit Insurance Corporation (FDIC) (the 'agencies') are issuing the attached Revised
Guidance on Model Risk Management."*

- URL: <https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm> — fetched 2026-09-20.

**Consequence for this repository.** None that is new: D-055 (2026-09-07) already ingested both
letters, marked SR 11-7 `superseded by SR26-2 on 2026-04-17` in `SOURCES.json`, made SR 26-2 the
drafter's default from Phase 8, and kept SR 11-7 in the corpus so that historical citations still
resolve. D-055 also fixes the wording this phase owes: the README says *"shaped after the
interagency model-validation guidance, SR 11-7 as revised by SR 26-2"*, and never "compliant" or
"certified". That is now done.

---

## 1. ValidMind

### 1.1 "a commercial model-risk-management platform"

**Verdict: CONFIRMED**, with a wording note.

- <https://validmind.com/platform/> — fetched 2026-09-20. Self-described as *"The Enterprise AI
  Governance Platform for regulated organizations deploying AI, GenAI, and agentic AI at scale."*
  Pricing nav, "Request a Demo" CTAs, a hosted SaaS app at `app.prod.validmind.ai`, and *"SaaS,
  on-prem, and customer-managed deployment options."*
- <https://validmind.com/about/> — fetched 2026-09-20. *"The AI Governance Platform."*

**Wording note:** they now position as an **AI-governance** platform rather than an MRM platform.
"Model-risk-management platform" is a fair description of what it does and is how it is discussed
in the market, but it is not the phrase on their own front page today. The README says "AI
governance platform" and describes the MRM workflow separately.

### 1.2 "automates SR 11-7 documentation and testing"

**Verdict: the automation half is CONFIRMED; the "SR 11-7" half is STALE and is not carried
forward.**

- The automation claim: <https://docs.validmind.com/> — fetched 2026-09-20 — describes the
  Development use case as *"Automating documentation and testing for your LLMs and other models."*
  <https://validmind.com/platform/automation/> — fetched 2026-09-20 — offers *"GenAI-assisted
  creation of validation reports, regulatory deliverables, and audit-ready documentation."*
- The regulatory naming: the same automation page names its targets as *"regulatory requirements
  (e.g., SR 26-2, E-23, SS1/23)"*. **SR 11-7 does not appear on that page.** The brief's phrasing
  is now a year out of date, for the same reason §0 above gives.
- SR 11-7 still appears on an older, still-live blog post,
  <https://validmind.com/blog/sr-11-7-model-risk-management-compliance/>, and a newer post bridges
  the two:
  <https://validmind.com/blog/sr-26-2-what-every-bank-needs-to-know-and-why-acting-now-is-a-competitive-advantage/>
  — *"SR 26-2 supersedes SR 11-7 as the primary supervisory guidance on model risk management for
  U.S. banking organizations."*

**Not carried forward.** The README says ValidMind automates documentation and testing against
SR 26-2, not SR 11-7.

### 1.3 "sold to banks"

**Verdict: CONFIRMED.**

- <https://validmind.com/> — fetched 2026-09-20 — *"AI governance platform purpose-built for
  regulated industries, including banking and insurance"*, with dedicated Banking and Insurance
  solution pages.
- <https://validmind.com/about/> — fetched 2026-09-20 — helps *"banks and insurers to deploy AI and
  GenAI safely, at scale, and in compliance with evolving global regulations."*
- Case study: <https://validmind.com/blog/validmind-case-study-general-bank-of-canada/>.
- Third-party: <https://finovate.com/experian-selects-validmind-to-help-banks-manage-ai-compliance/>
  — "Experian Selects ValidMind to Help Banks Manage AI Compliance."

### 1.4 "increasingly LLM-assisted"

**Verdict: CONFIRMED**, and now specific enough to name features.

<https://docs.validmind.com/about/overview-llm-features.html> — fetched 2026-09-20 — lists four
named LLM-powered features:

| feature | what the page says it does |
|---|---|
| Test Interpretation | *"generates a description of the tests, highlights key insights from the outcomes, and provides a summary with actionable takeaways"* |
| Qualitative Checks | creates *"qualitative sections within documentation"* from inventory metadata and test outcomes |
| Risk Assessment | *"generates a tailored risk assessment for each section of documentation"* from test-result data |
| ValidMind Document Checker | *"Reviews documents such as documentation or validation reports to ensure documents align with relevant regulatory requirements"* |

A fifth, "Content Builder" (chat-based drafting), appears in a search snippet of
<https://validmind.com/blog/feature-highlight-complete-control-over-model-documentation/> but that
page was **not independently fetched**; it is recorded here at lower confidence and is not used in
the README.

**Note for this project.** The Document Checker is the nearest thing in the market to Quaestor's
verifier, but it checks a document against *regulatory requirements*, not numbers against
*computed artifacts*. That is the distinction the README draws.

### 1.5 "it is closed and enterprise"

**Verdict: WRONG as stated. Not carried forward.**

ValidMind publishes open-source code:

- **ValidMind Library** — <https://github.com/validmind/validmind-library> — fetched 2026-09-20.
  *"ValidMind's Library contains a suite of developer tools and methods designed to run validation
  tests and automate the documentation of your models."* Its LICENSE
  (<https://github.com/validmind/validmind-library/blob/main/LICENSE>, fetched 2026-09-20) states:
  *"This software is dual-licensed under the GNU Affero General Public License version 3 (AGPL-3.0)
  and the ValidMind Commercial License."* A user may choose either. Also on PyPI at
  <https://pypi.org/project/validmind/> — **that page would not load for me today** (two attempts,
  browser/network error), so its classifier text is not quoted here; the GitHub LICENSE file is
  treated as authoritative.
- **Atryum** — <https://github.com/validmind/atryum> — an open-source control layer for AI agents,
  **Apache-2.0**, announced 2026-06-15
  (<https://www.prnewswire.com/news-releases/validmind-launches-atryum-a-new-open-source-control-layer-for-ai-agents-and-opens-early-access-to-validmind-agent-authority-302798691.html>).

The GitHub org <https://github.com/validmind> carries four public repos: `documentation`,
`validmind-library`, `atryum`, `.github`.

**The accurate statement**, and the one the README uses: the hosted platform is proprietary and
enterprise-sold; the client-side testing and documentation library, and the newer agent-governance
layer, are dual-licensed with a real open-source path.

### 1.6 Does ValidMind publish a measured detection rate against seeded defects, or a grounding-precision metric?

**Verdict: NOT FOUND — and stated as "not found", never as "they do not".**

- <https://validmind.com/ai-testing-results/> — fetched 2026-09-20 — is the closest thing. It
  reports LLM-evaluation metrics for their own governance tasks: **Faithfulness**, **Answer
  Relevancy**, **Verbosity**, and cost/latency. On Faithfulness: *"measur[es] how consistently a
  response stays grounded in the provided inputs. Outputs are assessed statement by statement to
  determine whether claims can be traced back to source material."* That is a grounding-shaped
  metric over source text — it is **not** a detection rate against planted defects, and it does
  not match numbers against a computed artifact store.
- Searched: `site:validmind.com` for precision / recall / false-positive rate; "ValidMind detection
  rate seeded defects"; "ValidMind grounding precision". No seeded-defect study surfaced.
- **This is a negative search result, not proof of absence.** Their blog archive was not read
  exhaustively.

### 1.7 Recent changes as of 2026

- SR 11-7 → SR 26-2, and ValidMind has already repositioned around SR 26-2 (§1.2).
- **Atryum** launched open source (Apache-2.0) with a commercial "Agent Authority" layer above it,
  2026-06-15 (URL in §1.5).
- Chartis named ValidMind #1 AI Governance Platform in the 2026 RiskTech100, February 2026 —
  <https://validmind.com/news/chartis-names-validmind-the-no-1-ai-governance-platform-in-2026-risktech100/>.
- No acquisition or rebrand found.

### 1.8 Reachability

`docs.validmind.ai` — the domain `01-BRIEF.md` §3 implicitly points at — is now a **legacy domain**.
Fetches of specific paths under it returned a bare "Redirect" with no destination captured. The
live documentation is at **`docs.validmind.com`**, and that is the domain cited above.

---

## 2. deepchecks

### 2.1 "open source"

**Verdict: CONFIRMED, but NEEDS QUALIFICATION — the company was acquired and the project has
shipped nothing for ~21 months.**

- <https://github.com/deepchecks/deepchecks> — fetched 2026-09-20. *"Deepchecks is a holistic
  open-source solution for all of your AI & ML validation needs."* 4,056 stars. **Not archived.**
- License: <https://raw.githubusercontent.com/deepchecks/deepchecks/main/LICENSE> — fetched
  2026-09-20 — is **GNU AGPL v3**, with an added commercial carve-out for the separate Monitoring
  sub-library. (GitHub's auto-detected license field via
  <https://api.github.com/repos/deepchecks/deepchecks> reads `"Other (NOASSERTION)"`, most likely
  because the modified dual text defeats the detector; the LICENSE file itself is unambiguous.)
- **Last PyPI release: 0.19.1, 2024-12-15** — <https://pypi.org/project/deepchecks/>, fetched
  2026-09-20. That is 21 months ago as of today.
- Last visible commit on `main`: **2025-11-24** (`fix-lang-nan-indices #2807`),
  <https://github.com/deepchecks/deepchecks/commits/main>; the API's `pushed_at` reads
  `2025-12-28T12:07:44Z`.
- **Acquisition.** Check Point Software Technologies acquired Deepchecks — team and IP — reported
  2026-05-19 by Calcalist (<https://www.calcalistech.com/ctechnews/article/hku7df9jfg>: *"buying the
  team and intellectual property of startup Deepchecks"*) and 2026-05-20 by BankInfoSecurity
  (<https://www.bankinfosecurity.com/check-point-validates-ai-driven-actions-deepchecks-buy-a-31740>,
  deal estimated $10–20M, terms undisclosed). Neither article addresses the fate of the OSS repo.
  No commits are visible after the acquisition date.

**The accurate statement:** still open source and unarchived under AGPLv3, but independent
development looks paused or absorbed post-acquisition. "Actively maintained" cannot be asserted.

### 2.2 "runs component-level data and model checks (drift, leakage, performance suites)"

**Verdict: CONFIRMED**, at the level of named checks rather than marketing copy.

- <https://deepchecks.com/open-source/> — fetched 2026-09-20 — names the **Data Integrity Suite**
  (*"conflicting labels or data duplicates"*), the **Train-Test Validation Suite** (*"examines
  whether separate datasets are representative of each other"*), and the **Model Evaluation Suite**
  (*"tests model performance and identifies underperforming segments"*), plus NLP and vision
  suites; it says datasets are checked for *"issues such as drift or leakage"*.
- <https://docs.deepchecks.com/stable/tabular/auto_tutorials/quickstarts/plot_quick_train_test_validation.html>
  — fetched 2026-09-20 — lists the Train-Test Validation suite's twelve actual checks, which
  include **Feature Drift, Label Drift, Multivariate Drift** and **Index Leakage, Date Train Test
  Leakage Overlap, Date Train Test Leakage Duplicates**. Both drift and leakage checks exist by
  name.

This is the claim the brief gets exactly right, and it is the substantive overlap with Quaestor:
deepchecks' drift and leakage suites cover roughly the ground Quaestor's `profile_data` and
`check_leakage` cover.

### 2.3 "drafts no grounded validation report"

**Verdict: CONFIRMED for the open-source library. NEEDS QUALIFICATION — there is now a commercial
LLM-evaluation product whose output I could not fully characterise.**

- Output format, from the same quickstart page: results are a `SuiteResult` shown in a notebook and
  exported with `suite_result.save_as_html()` or `.to_json()`. <https://deepchecks.com/open-source/>
  describes outputs as *"displayed in a notebook and/or conditions with a pass/fail output"* feeding
  *"reports (testing module) and the dashboards (monitoring module)"*. That is a check-by-check
  pass/fail artifact, not a narrative document in which each number carries a citation.
- **Qualification.** <https://deepchecks.com/> — fetched 2026-09-20 — now prominently markets a
  separate commercial **"Deepchecks LLM Evaluation Platform"**: *"enterprise-grade AI testing,
  observability, and monitoring"*, with auto-scoring, LLM judges, agent and version comparison, and
  production tracing. On the pages reached, nothing describes it producing a narrative validation
  report with inline citations to computed evidence — but that is **not found**, not verified
  absent. The README therefore scopes this claim to the open-source library.

### 2.4 "follows no regulatory structure"

**Verdict: NEEDS QUALIFICATION. The flat claim is too strong and is softened in the README.**

- Neither **"SR 11-7"** nor **"SR 26-2"** nor "Federal Reserve" appears anywhere on deepchecks.com
  in the searches run.
- **But** they publish content explicitly about bank model-risk regulation:
  <https://www.deepchecks.com/top-5-components-for-model-risk-management/> — fetched 2026-09-20 —
  is framed entirely around Model Risk Management and quotes the **OCC's 2011 supervisory
  guidance**: *"All banks should confirm that their practices conform to the principles in this
  guidance for model development, implementation, and use, as well as model validation."* It never
  names SR 11-7 or the Fed.
- <https://deepchecks.com/> also markets SOC 2 Type 2, GDPR, HIPAA, SSO and AWS GovCloud — general
  security and data-residency compliance positioning, not MRM report structure.

**The accurate statement:** deepchecks writes about bank MRM and markets to regulated industries,
but it does not claim conformance to the model-validation guidance, does not structure its output
around that guidance's sections, and its product output is a pass/fail suite result rather than a
validation document.

### 2.5 Does deepchecks publish a measured detection rate against seeded defects?

**Verdict: NOT FOUND, with one source unread.**

- Searched `docs.deepchecks.com`, the deepchecks.com blog, the GitHub README and the PyPI
  description. No detection rate, precision/recall figure, or seeded-defect benchmark surfaced.
- **One genuine gap:** their JMLR paper, <https://www.jmlr.org/papers/volume23/22-0281/22-0281.pdf>,
  could not be read — the fetch returned raw compressed stream data rather than text. A benchmark
  section in that paper is neither confirmed nor ruled out. Recorded as unverified rather than as a
  negative.

### 2.6 Reachability

<https://docs.deepchecks.com/stable/tabular/auto_checks/index.html> returned **HTTP 404**. The
equivalent check listing was taken from the working quickstart URL in §2.2 rather than guessed.

---

## 3. The others named in the brief

`01-BRIEF.md` §3 also names **Openlayer, ModelOp and CIMCON** as "adjacent commercial MRM and
governance space". They were **not checked today**, because the README does not make a claim about
any of them. Under §12's reject rule, an unverified comparison must not be published; the
resolution is to not publish it. If a future README names them, they get rows here first.

The brief's research claim — that *"LLM-as-validator for model risk does not have a public,
evaluated artifact"* — is a negative over the whole literature and is **not carried into the
README** in that form. What the README says instead is what this file can support: that no
detection rate against seeded defects and no per-report grounding precision was found published by
either vendor checked, with the search recorded and its limits stated.

FinQA and TAT-QA are used here only as a source of arithmetic-answer items to test the claim
verifier as a component, which is what §3 says, and no claim about them needed checking.

---

## 4. Summary of what changed between the brief and today

| brief §3 claim | status 2026-09-20 | in the README? |
|---|---|---|
| SR 11-7 is the governing guidance | superseded by SR 26-2 on 2026-04-17 | corrected: "SR 11-7 as revised by SR 26-2" |
| ValidMind is commercial MRM, sold to banks | confirmed (they say "AI governance") | yes, with their own wording |
| ValidMind automates SR 11-7 documentation and testing | automation confirmed; SR 11-7 stale | yes, against SR 26-2 |
| ValidMind increasingly LLM-assisted | confirmed, four named features | yes |
| ValidMind is closed and enterprise | **wrong** — AGPL-3.0 library, Apache-2.0 Atryum | corrected |
| deepchecks is open source | confirmed (AGPLv3); acquired by Check Point 2026-05 | yes, with the acquisition |
| deepchecks runs drift / leakage / performance checks | confirmed by name | yes |
| deepchecks drafts no grounded validation report | confirmed for the OSS library | yes, scoped to the library |
| deepchecks follows no regulatory structure | too strong | softened |
| neither publishes a seeded-defect detection rate | not found, searches recorded | yes, stated as "not found" |
