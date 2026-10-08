import os

from rag.rag_engine import ElectricalRAG


PDF_PATH = "knowledge/textbooks/Theraja_V2.pdf"

INDEX_PATH = "knowledge/index/Theraja_V2.faiss"

METADATA_PATH = "knowledge/index/Theraja_V2.json"


rag = ElectricalRAG()


# ---------------------------------
# Check for existing knowledge base
# ---------------------------------

if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):

    print("Existing knowledge base found.")

    rag.load_index(
        INDEX_PATH,
        METADATA_PATH
    )

else:

    print(
        "No existing knowledge base found."
    )

    print(
        "Starting one-time PDF ingestion..."
    )

    # OCR / text extraction
    chunks = rag.load_pdf(
        PDF_PATH
    )

    print(
        f"Loaded {chunks} chunks."
    )

    # Create embeddings + FAISS
    indexed = rag.build_index()

    print(
        f"Indexed {indexed} chunks."
    )

    # Save everything
    rag.save_index(
        INDEX_PATH,
        METADATA_PATH
    )


# ---------------------------------
# Ask question
# ---------------------------------

question = input("\nAsk an Electrical Engineering question: ")

print("\n================================")
print("RETRIEVED CHUNKS")
print("================================\n")

results = rag.retrieve(question, k=4)

for i, result in enumerate(results, start=1):
    print(f"\n--- RESULT {i} ---")
    print(f"Source: {result['source']}")
    print(f"Page: {result['page']}")
    print(f"Distance: {result['distance']}")
    print("\nTEXT:")
    print(result["text"])


print("\n================================")
print("ANSWER")
print("================================\n")

result = rag.answer(question)
print(
    result["answer"]
)


print("\n================================")
print("SOURCES")
print("================================\n")

for source in result["sources"]:

    print(
        f"- {source['source']} "
        f"(Page {source['page']})"
    )