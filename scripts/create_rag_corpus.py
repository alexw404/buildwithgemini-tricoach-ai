"""Script to create a serverless Vertex AI RAG Engine corpus and import pg49513.txt."""

import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-01-57b0d8b0ef08"
LOCATION = "us-central1"
GCS_PATH = "gs://tricoach-ai-media-57b0d8b0ef08/rag/pg49513.txt"

vertexai.init(project=PROJECT_ID, location=LOCATION)

print("Configuring serverless RAG Engine DB...")
cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
rag.update_rag_engine_config(
    rag_engine_config=rag.RagEngineConfig(
        name=cfg,
        rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
    )
)

print("Creating serverless corpus...")
corpus = rag.create_corpus(
    display_name="pg49513-corpus",
    embedding_model_config=rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-005"
    ),
)
print("CREATED_CORPUS_NAME:", corpus.name)

print("Importing document from GCS into corpus...")
resp = rag.import_files(
    corpus_name=corpus.name,
    paths=[GCS_PATH],
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
    ),
)
print("IMPORTED_FILES_COUNT:", resp.imported_rag_files_count)
