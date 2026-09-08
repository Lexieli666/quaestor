"""``retrieve_guidance``: the ninth tool, and the only one that computes nothing about the model.

Spec section 3.7's last row. It runs BM25 (:mod:`quaestor.corpus.bm25`) over the committed
regulatory corpus and stores the retrieved spans as one JSON artifact, ``guidance.<query_hash>``.
It raises no finding candidate and it can raise none: guidance is what a section is *anchored* to,
not evidence that something is wrong with a model, and a tool that turned a retrieval into a
finding would be inventing a defect out of a search result.

The artifact matters as much as the return value. The drafter is given these spans in its prompt
(spec section 3.11) and writes a ``[[reg:DOC:SECTION]]`` citation from them; the verifier resolves
that citation against the same corpus. Storing the retrieval means the trace records which text
the drafter was shown, so a report anchored to the wrong section is diagnosable after the fact
without re-running anything.

``k`` is **per document**: the corpus holds the superseded SR 11-7 and the SR 26-2 revision that
replaced it, BM25 scores do not compare across two documents, and a single ranked list therefore
chose the drafter's anchor by term frequency rather than by currency (DECISIONS D-108). Each
document's own best ``k`` are returned, the current guidance's first, and which one to cite is the
drafter's decision under D-055.

The logical name carries a hash of the whole request -- query, ``k`` and the document restriction
-- rather than a slug of the query, because two sections of a report ask for guidance in words
that slugify identically far more often than they hash identically, and the store refuses to put a
different payload under a name it already holds (DECISIONS D-059).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from ..artifacts import Artifact, ArtifactKind
from ..corpus import CORPUS_FILES, ScoredSpan, retrieve, scored_payload
from ..errors import CorpusError, ToolError
from ..hashing import stable_hash
from .registry import Tool, ToolArgs, ToolContext, ToolResult

__all__ = ["CURRENT_GUIDANCE", "RetrieveGuidanceTool", "guidance_name", "retrieve_per_document"]

CURRENT_GUIDANCE: Final = "SR26-2"
"""The current guidance, whose spans are returned first (D-055)."""


def retrieve_per_document(query: str, k: int, docs: Sequence[str] | None) -> list[ScoredSpan]:
    """Retrieve the best ``k`` spans **of each document** searched, current guidance first.

    BM25 scores are comparable within a document and not across two documents of different length
    and vocabulary, and the corpus holds a superseded text and the revision that replaced it
    (D-055). Ranking them in one list therefore decides which document a section anchors to by an
    accident of term frequency: on the fourth live run the data-quality, sensitivity and
    findings queries each returned three SR 11-7 spans and no SR 26-2 span at all, so sections 3
    and 5 opened on superseded text while SR 26-2 IV.1 and V.1.a sat in the corpus unretrieved.
    Retrieving per document makes the choice the drafter's, which is where D-055 and
    ``DRAFT_INSTRUCTION`` already put it -- "prefer a span of the current guidance; cite the
    superseded text only where it says something the revision does not" -- and gives it something
    to prefer (DECISIONS D-108).

    Args:
        query: What to look for.
        k: How many spans to return **per document**.
        docs: The documents to search, or ``None`` for the whole corpus.

    Returns:
        The spans, the current guidance's first and each document's own best first. A document
        that shares no term with the query contributes nothing.

    Raises:
        CorpusError: ``docs`` names a document that was never ingested, or the corpus is missing.
    """
    searched = list(docs) if docs is not None else list(CORPUS_FILES)
    ordered = [doc for doc in searched if doc == CURRENT_GUIDANCE] + [
        doc for doc in searched if doc != CURRENT_GUIDANCE
    ]
    return [span for doc in ordered for span in retrieve(query, k, [doc])]


def guidance_name(query: str, k: int, docs: list[str] | None) -> str:
    """Return the logical name a retrieval is stored under.

    Args:
        query: The query as asked.
        k: How many spans were asked for.
        docs: The document restriction, or ``None``.

    Returns:
        ``guidance.<query_hash>``, where the hash is a :func:`~quaestor.hashing.stable_hash` of
        the whole request, so that the same request in the same run resolves to the same artifact
        and a different one cannot collide with it.
    """
    return f"guidance.{stable_hash({'query': query, 'k': k, 'docs': docs})}"


class RetrieveGuidanceTool(Tool["RetrieveGuidanceTool.Args"]):
    """Retrieve the sections of the model-risk guidance that bear on a question."""

    name = "retrieve_guidance"
    description = (
        "Search the committed regulatory corpus (SR 11-7 and its 2026 revision SR 26-2) with "
        "BM25 and return the best-matching sections, so a report section can be anchored to the "
        "guidance with a [[reg:DOC:SECTION]] citation."
    )

    class Args(ToolArgs):
        """Arguments of ``retrieve_guidance``.

        Attributes:
            query: What to look for, in plain words -- ``"outcomes analysis"``,
                ``"benchmarking against a challenger model"``.
            k: How many spans to return **per document searched**, at most. Two documents and
                ``k=3`` return at most six spans, the current guidance's three first (D-108).
            docs: Restrict the search to these documents; ``None`` searches both. ``SR26-2`` is
                the current guidance and ``SR11-7`` the superseded text kept so that historical
                citations resolve (DECISIONS D-055).
        """

        query: str
        k: int = 3
        docs: list[str] | None = None

    def run(self, args: RetrieveGuidanceTool.Args, ctx: ToolContext) -> ToolResult:
        """Retrieve the spans, store them as one JSON artifact and return them.

        Args:
            args: The query, how many spans to return, and any document restriction.
            ctx: The run's context.

        Returns:
            One artifact, ``guidance.<query_hash>``, holding the spans with their scores -- the
            best ``k`` of each document, the current guidance's first (D-108). No finding
            candidate, ever.

        Raises:
            ToolError: The query is empty, ``k`` is not positive, ``docs`` names a document that
                is not in the corpus, or the corpus is missing or malformed.
        """
        query = args.query.strip()
        if not query:
            raise ToolError("retrieve_guidance needs a query; an empty one retrieves nothing")
        if args.k < 1:
            raise ToolError(f"retrieve_guidance was asked for k={args.k}; k must be at least 1")
        try:
            spans = retrieve_per_document(query, args.k, args.docs)
        except CorpusError as exc:
            raise ToolError(
                f"retrieve_guidance cannot search the regulatory corpus: {exc.message}",
                fix=exc.fix,
            ) from exc

        name = guidance_name(query, args.k, args.docs)
        payload = {
            "query": query,
            "k": args.k,
            "docs": args.docs if args.docs is not None else list(CORPUS_FILES),
            "spans": scored_payload(spans),
        }
        cited = ", ".join(span.citation for span in spans) or "nothing"
        artifact: Artifact = ctx.store.put(
            name,
            payload,
            ArtifactKind.json,
            f"guidance retrieved for {query!r}: {cited}",
        )
        return ToolResult(
            tool=self.name,
            artifacts=[artifact],
            candidates=[],
            summary=(
                f"{len(spans)} span(s) for {query!r}: {cited}"
                if spans
                else f"no section of the corpus shares a term with {query!r}"
            ),
        )
