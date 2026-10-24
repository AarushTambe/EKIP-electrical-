from rag.rag_engine import ElectricalRAG


INDEX_PATH = "knowledge/index/Theraja_V2.faiss"
METADATA_PATH = "knowledge/index/Theraja_V2.json"

QUESTION = input(
    "Enter an Electrical Engineering question to test: "
).strip()

while not QUESTION:
    print("Question cannot be empty.")
    QUESTION = input(
        "Enter an Electrical Engineering question to test: "
    ).strip()


def main():
    print("Loading EKIP RAG system...")

    rag = ElectricalRAG()

    if not rag.load_index(
        INDEX_PATH,
        METADATA_PATH,
    ):
        raise RuntimeError(
            "Could not load the existing knowledge base."
        )

    print(
        f"Knowledge base loaded: "
        f"{len(rag.documents)} chunks"
    )

    print("\nRunning the same question three times...\n")

    results = []

    for i in range(3):

        print(f"--- Run {i + 1} ---")

        result = rag.answer(
            QUESTION,
            chat_history=[],
        )

        results.append(result)

        print("Answer:")
        print(result["answer"])

        print("\nSources:")

        for source in result["sources"]:
            print(
                f"- {source['source']} "
                f"Page {source['page']}"
            )

        print()

    # --------------------------------------------------------
    # Compare retrieved sources
    # --------------------------------------------------------

    source_sets = []

    for result in results:

        sources = tuple(
            (
                source["source"],
                source["page"],
            )
            for source in result["sources"]
        )

        source_sets.append(sources)

    retrieval_consistent = (
        source_sets[0]
        == source_sets[1]
        == source_sets[2]
    )

    # --------------------------------------------------------
    # Compare generated answers
    # --------------------------------------------------------

    answers = [
        result["answer"]
        for result in results
    ]

    answer_consistent = (
        answers[0]
        == answers[1]
        == answers[2]
    )

    print("=" * 60)
    print("CONSISTENCY RESULTS")
    print("=" * 60)

    print(
        f"Retrieval consistent: "
        f"{retrieval_consistent}"
    )

    print(
        f"Answer text consistent: "
        f"{answer_consistent}"
    )

    if retrieval_consistent:
        print(
            "\n✓ FAISS returned the same sources "
            "for all three runs."
        )
    else:
        print(
            "\n⚠ FAISS returned different sources "
            "between runs."
        )

    if answer_consistent:
        print(
            "✓ Mistral produced the same answer "
            "for all three runs."
        )
    else:
        print(
            "⚠ Mistral produced different answer "
            "text between runs."
        )

    print("=" * 60)

    # We are measuring behavior here.
    # Do not fail the test merely because Mistral
    # produces different wording.
    print(
        "\nPhase 2.9 consistency measurement complete."
    )


if __name__ == "__main__":
    main()