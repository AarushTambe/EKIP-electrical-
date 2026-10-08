import os
import io
import json
import faiss
import numpy as np
import pytesseract
import pymupdf

from PIL import Image

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_text_splitters import CharacterTextSplitter


# Tell pytesseract where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class ElectricalRAG:

    def __init__(self):

        # -----------------------------
        # Models
        # -----------------------------

        self.llm = OllamaLLM(
            model="mistral"
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # -----------------------------
        # FAISS
        # -----------------------------

        self.embedding_dimension = 384

        self.index = faiss.IndexFlatL2(
            self.embedding_dimension
        )

        # Each item corresponds to
        # one vector in FAISS
        self.documents = []

        # -----------------------------
        # Text splitter
        # -----------------------------

        self.splitter = CharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100
        )

    # =================================
    # LOAD PDF
    # =================================

    def load_pdf(self, pdf_path):

        print(f"\nLoading: {pdf_path}")

        pdf = pymupdf.open(pdf_path)

        chunks_added = 0

        for page_number, page in enumerate(
            pdf,
            start=1
        ):

            # -----------------------------
            # Try normal text extraction
            # -----------------------------

            text = page.get_text(
                "text"
            ).strip()

            # -----------------------------
            # If scanned → OCR
            # -----------------------------

            if not text:

                print(
                    f"Page {page_number}: "
                    f"No text found → running OCR..."
                )

                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2)
                )

                image_bytes = pix.tobytes(
                    "png"
                )

                image = Image.open(
                    io.BytesIO(image_bytes)
                )

                text = pytesseract.image_to_string(
                    image
                ).strip()

            # -----------------------------
            # Skip empty pages
            # -----------------------------

            if not text:

                print(
                    f"Page {page_number}: "
                    f"No readable text."
                )

                continue

            # -----------------------------
            # Split text
            # -----------------------------

            chunks = self.splitter.split_text(
                text
            )

            # -----------------------------
            # Store chunks
            # -----------------------------

            for chunk in chunks:

                self.documents.append({
                    "text": chunk,
                    "source": os.path.basename(
                        pdf_path
                    ),
                    "page": page_number
                })

                chunks_added += 1

        pdf.close()

        print(
            "\nFinished processing PDF."
        )

        print(
            f"Total chunks created: "
            f"{chunks_added}"
        )

        return chunks_added

    # =================================
    # BUILD FAISS INDEX
    # =================================

    def build_index(self):

        if not self.documents:

            raise ValueError(
                "No documents have been loaded."
            )

        print(
            "\nCreating embeddings..."
        )

        texts = [
            document["text"]
            for document in self.documents
        ]

        vectors = self.embeddings.embed_documents(
            texts
        )

        vectors = np.array(
            vectors,
            dtype=np.float32
        )

        print(
            "Adding embeddings to FAISS..."
        )

        self.index.add(
            vectors
        )

        print(
            f"FAISS index contains "
            f"{self.index.ntotal} vectors."
        )

        return len(texts)

    # =================================
    # SAVE INDEX
    # =================================

    def save_index(
        self,
        index_path,
        metadata_path
    ):

        print("\nSaving FAISS index...")

        # Save vectors
        faiss.write_index(
            self.index,
            index_path
        )

        # Save chunks + metadata
        with open(
            metadata_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.documents,
                file,
                ensure_ascii=False,
                indent=2
            )

        print(
            f"FAISS index saved to: "
            f"{index_path}"
        )

        print(
            f"Metadata saved to: "
            f"{metadata_path}"
        )

    # =================================
    # LOAD INDEX
    # =================================

    def load_index(
        self,
        index_path,
        metadata_path
    ):

        if not os.path.exists(
            index_path
        ):

            return False

        if not os.path.exists(
            metadata_path
        ):

            return False

        print(
            "\nLoading existing knowledge base..."
        )

        # Load FAISS
        self.index = faiss.read_index(
            index_path
        )

        # Load metadata
        with open(
            metadata_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.documents = json.load(
                file
            )

        print(
            f"Loaded {len(self.documents)} "
            f"chunks."
        )

        print(
            f"FAISS contains "
            f"{self.index.ntotal} vectors."
        )

        return True

    # =================================
    # RETRIEVE
    # =================================

    def retrieve(
        self,
        query,
        k=4
    ):

        if self.index.ntotal == 0:

            return []

        query_vector = (
            self.embeddings.embed_query(
                query
            )
        )

        query_vector = np.array(
            [query_vector],
            dtype=np.float32
        )

        k = min(
            k,
            self.index.ntotal
        )

        distances, indices = (
            self.index.search(
                query_vector,
                k
            )
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            if index < 0:
                continue

            document = (
                self.documents[index].copy()
            )

            document["distance"] = float(
                distance
            )

            results.append(
                document
            )

        return results

        # =================================
    # ANSWER
    # =================================

    def answer(self, query, chat_history=None):

        # ---------------------------------
        # Build conversation text
        # ---------------------------------

        history_text = ""

        if chat_history:

            history_text = "\n".join(
                [
                    f"{message['role'].capitalize()}: "
                    f"{message['content']}"
                    for message in chat_history
                ]
            )

        # ---------------------------------
        # Create standalone retrieval query
        # ---------------------------------

        if chat_history:

            retrieval_prompt = f"""
You are helping an Electrical Engineering textbook
retrieval system.

Rewrite the student's CURRENT QUESTION into a
short, standalone search query that can be used
to search an Electrical Engineering textbook.

Use the conversation history to resolve references
such as:

- it
- its
- this
- that
- they
- their
- the above
- previous question
- first question
- second question
- same topic

IMPORTANT:

1. Preserve the actual subject of the student's question.

2. If the current question is already self-contained,
   do not unnecessarily change its meaning.

3. If the question refers to something earlier,
   resolve that reference using the conversation.

4. Ignore unrelated earlier topics.

5. Return ONLY the search query.

CONVERSATION HISTORY:
{history_text}

CURRENT QUESTION:
{query}

SEARCH QUERY:
"""

            retrieval_query = self.llm.invoke(
                retrieval_prompt
            ).strip()

        else:

            retrieval_query = query

        # ---------------------------------
        # Retrieve textbook chunks
        # ---------------------------------

        results = self.retrieve(
            retrieval_query,
            k=8
        )

        # ---------------------------------
        # Relevance filtering
        # ---------------------------------

        relevant_results = [
            result
            for result in results
            if result["distance"] <= 0.90
        ]

        # ---------------------------------
        # No relevant textbook context
        # ---------------------------------

        if not relevant_results:

            return {
                "answer": (
                    "I couldn't find sufficient information "
                    "about this question in the provided "
                    "Electrical Engineering textbook."
                ),
                "sources": []
            }

        # ---------------------------------
        # Build textbook context
        # ---------------------------------

        context_parts = []
        sources = []

        for document in relevant_results[:4]:

            context_parts.append(
                f"[Source: {document['source']}, "
                f"Page: {document['page']}]\n"
                f"{document['text']}"
            )

            sources.append({
                "source": document["source"],
                "page": document["page"]
            })

        context = "\n\n".join(
            context_parts
        )

        # ---------------------------------
        # Final answer prompt
        # ---------------------------------

        prompt = f"""
You are an Electrical Engineering AI Tutor.

Answer the student's CURRENT QUESTION using the
provided textbook context and conversation history.

RULES:

1. Use the textbook context as the primary source.

2. Use the conversation history to understand
   follow-up questions and references.

3. Do not invent information that is not supported
   by the textbook context.

4. If the textbook context does not contain enough
   information, clearly say so.

5. Answer naturally and directly.

6. Do not unnecessarily repeat previous answers.

7. Give explanations suitable for an
   Electrical Engineering student.

8. Use equations where appropriate.

CONVERSATION HISTORY:
{history_text}

TEXTBOOK CONTEXT:
{context}

CURRENT STUDENT QUESTION:
{query}

Answer:
"""

        # ---------------------------------
        # Generate answer
        # ---------------------------------

        response = self.llm.invoke(
            prompt
        )

        # ---------------------------------
        # Return result
        # ---------------------------------

        return {
            "answer": response,
            "sources": sources
        }