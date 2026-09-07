"""The regulatory corpus: ingest, section ids and a hand-written BM25.

Empty in Phase 0; filled in Phase 6 from spec section 3.8. The two source PDFs are public U.S.
government documents that the human downloads outside the repository; ``pypdf`` reads them at
ingest time only and is a development dependency (DECISIONS D-001). The resulting JSONL files are
committed, and a ``[[reg:SR11-7:V.3]]`` citation resolves against their ``section_id``.
"""
