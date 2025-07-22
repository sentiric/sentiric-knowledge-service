# Sentiric Knowledge Service

**Description:** Creates and manages a structured, searchable knowledge base for Sentiric's AI agents, enabling them to retrieve relevant information.

**Core Responsibilities:**
*   Ingesting and processing data from various external sources (databases, documents, CRM, websites).
*   Normalizing, transforming, and indexing data into suitable formats (e.g., vector embeddings, search indexes).
*   Providing APIs for AI agents to quickly query and retrieve knowledge.
*   Managing underlying knowledge storage technologies (e.g., vector databases like Pinecone, search engines like Elasticsearch).

**Technologies:**
*   Python (or Java)
*   Flask/FastAPI (for REST API)
*   Libraries for data processing, natural language processing (NLP), vector embeddings.
*   Integration with database/search technologies (e.g., PostgreSQL, Elasticsearch, Pinecone).
* we can use Sentence Transformers (all-MiniLM-L6-v2) + FAISS 

**API Interactions (As an API Provider):**
*   Exposes a RESTful API for `sentiric-agent-service` to query information.
*   Consumes data from `sentiric-connectors` to ingest and update knowledge.

**Local Development:**
1.  Clone this repository: `git clone https://github.com/sentiric/sentiric-knowledge-service.git`
2.  Navigate into the directory: `cd sentiric-knowledge-service`
3.  Create a virtual environment and install dependencies: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
4.  Create a `.env` file from `.env.example` (if any), especially for database/indexer connections.
5.  Start the service: `python app.py` (or equivalent).

**Configuration:**
Refer to `config/` directory and `.env.example` for service-specific configurations, including external data source connections and knowledge base settings.

**Deployment:**
Designed for containerized deployment (e.g., Docker, Kubernetes), potentially requiring significant storage and processing power for large knowledge bases. Refer to `sentiric-infrastructure`.

**Contributing:**
We welcome contributions! Please refer to the [Sentiric Governance](https://github.com/sentiric/sentiric-governance) repository for coding standards and contribution guidelines.

**License:**
This project is licensed under the [License](LICENSE).
