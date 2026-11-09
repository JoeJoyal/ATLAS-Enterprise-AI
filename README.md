# ATLAS-Enterprise-AI
production based rag pipeline

conda create -n altas python=3.12 -y

activate altas

**Implementation Steps:**

- **Phase 1** - **Infrastructure:** Environment, PostgreSQL, AWS, and Pinecone.
- **Phase 2** - **AI Engineering:** RAG, Memory, Guardrails, Observability, HITL, and LangGraph.
- **Phase 3** - **Full-Stack Application:** API, HTML, CSS, and JavaScript.
- **Phase 4** - **Integration and Testing:** S3, CORS, tests, documentation, and end-to-end-demonstration.


SQLTools in vscode extension
SQLTools PostgreSQL/Cockroach Driver


S3 bucket cors configuration:
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["PUT"],
        "AllowedOrigins": [
            "http://127.0.0.1:8000",
            "http://localhost:8000"
        ],
        "ExposeHeaders": ["ETag"],
        "MaxAgeSeconds": 3000
    }
]