# MediVault — GenAI-Powered Personal Health Record Vault

**Idea Submission: Next-Generation GenAI Solutions**

---

## Problem Statement

Patients and caregivers struggle to get a clear, unified view of their health. Medical records are scattered across hospitals, labs, and clinics; documents are full of jargon; and there is no single place to ask “what did my doctor say about my condition?” or “summarize my last year of visits.” This fragmentation leads to repeated tests, missed follow-ups, and poor continuity of care.

**Who it impacts:** Patients (especially those with chronic conditions or multiple providers), family caregivers managing a loved one’s care, and clinicians who spend excessive time re-reading notes and chasing records.

---

## Motivation

- **Fragmentation:** Health data lives in silos—EHRs, lab portals, scanned PDFs, and wearables. Patients rarely have one place that “knows” their full story.
- **Gap:** Existing Personal Health Records (PHRs) are often view-only and not conversational. There is no widely adopted tool that lets users ask natural-language questions over their own medical history.
- **Opportunity:** Generative AI can turn a vault of documents into an intelligent, queryable health narrative—summarizing visits, translating jargon, and answering questions—while respecting privacy through on-device or private-cloud deployment and no training on user data.

---

## Application

- **Use case:** Users upload or connect medical documents (reports, discharge summaries, prescriptions, lab results). MediVault stores them securely and enables natural-language queries such as: “Summarize my diabetes-related visits in the last 6 months,” “What medications am I currently on?” and “Explain my latest lab results in simple terms.”
- **Target users:** Patients managing chronic conditions, family caregivers coordinating care, and optionally clinicians seeking a quick overview during referrals or second opinions.
- **Where applied:** Personal health management, pre-visit preparation, caregiver coordination, and patient empowerment in shared decision-making with providers.

---

## Proposed Method

- **GenAI approach:**
  - **Document ingestion:** Parse and chunk medical documents (PDF, structured FHIR/HL7 where available); extract text via OCR for images and scanned PDFs.
  - **Embeddings + RAG:** Use embedding models (e.g., open-source sentence/document embeddings) to index chunks; retrieve relevant chunks for each user query via semantic search.
  - **LLM layer:** Use a capable LLM (open-weight or API with appropriate compliance) for: (1) summarization of selected records, (2) Q&A with citations to source documents, (3) plain-language explanations. System prompts enforce medical disclaimers and “do not replace doctor” guidance.
  - **Privacy-first design:** Optional local or small LLM; no training on user data; explicit consent and access control (who can query whose vault).
- **Techniques:** Retrieval-Augmented Generation (RAG), chunking strategies for long documents, optional hybrid search (keyword + semantic), and citation grounding to reduce hallucination and improve trust.

---

## Datasets / Data Source

- **User-provided:** Medical documents (PDFs, images of reports)—sourced from real users with consent or synthetic data for demos and development.
- **Public medical text (evaluation only):** De-identified or synthetic Q&A pairs, or public datasets (e.g., MTS-Dialog, PubMedQA subset) to validate reasoning and safety—not for training on user data.
- **Medical terminology/ontologies (optional):** SNOMED, RxNorm, or UMLS subsets for entity recognition or normalization.
- **Availability:** User data remains user-owned (upload/sync). Public benchmarks and synthetic data are used for experiments. MVP does not depend on proprietary EHR data.

---

## Experiments

- **Retrieval quality:** Precision, recall, or Mean Reciprocal Rank (MRR) on “find the document/section that answers this question” over a held-out set of Q&A from synthetic or de-identified cases.
- **Generation quality:** Faithfulness (answers grounded in retrieved chunks), relevance (e.g., BERTScore or LLM-as-judge), and safety (no treatment advice, appropriate disclaimers).
- **End-to-end validation:** User studies or expert (e.g., clinician) review on a small set of summaries and Q&A for accuracy and usefulness.
- **Metrics:** Retrieval MRR/Recall@k; faithfulness (e.g., NLI-based or citation overlap); human ratings for clarity and medical appropriateness; latency and cost per query for feasibility.

---

## Novelty and Scope to Scale

- **Novelty:** Combines (1) a **patient-owned vault** where data stays with the user or tenant, (2) **conversational GenAI over personal medical history** via RAG with citations, and (3) **privacy-by-design** (no training on user data, optional local/private deployment). Emphasis on “my records, my questions, my consent.”
- **Scope to scale:**
  - **Vertical:** Expand from summaries and Q&A to medication reminders, pre-visit briefs, and integration with wearables and lab feeds.
  - **Horizontal:** Same vault + GenAI pattern can extend to clinical use (e.g., clinic-owned vault for a cohort) or consent-based research (aggregated, de-identified insights).
  - **Ecosystem:** Partnerships with EHR vendors, lab networks, or health systems for secure document ingestion (OAuth, FHIR) without centralizing raw data.
