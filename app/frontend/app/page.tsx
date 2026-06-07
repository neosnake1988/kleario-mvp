"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type DocumentRecord = {
  id: number;
  original_filename: string;
  document_type: string;
  issuer: string | null;
  document_date: string | null;
  amount: string | null;
  reference_number: string | null;
  proposed_file_name: string;
  proposed_folder: string;
  status: string;
  created_at: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [latestResult, setLatestResult] = useState<DocumentRecord | null>(null);
  const [query, setQuery] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const visibleDocuments = useMemo(() => documents, [documents]);

  useEffect(() => {
    void loadDocuments();
  }, []);

  async function loadDocuments() {
    setError(null);
    const response = await fetch(`${API_BASE_URL}/documents`);
    if (!response.ok) {
      setError("Unable to load documents.");
      return;
    }
    setDocuments(await response.json());
  }

  async function uploadDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      setError("Choose a PDF before uploading.");
      return;
    }

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: "POST",
      body: formData,
    });

    setIsUploading(false);

    if (!response.ok) {
      setError(
        await getApiErrorMessage(response, "The PDF could not be processed."),
      );
      return;
    }

    const result = (await response.json()) as DocumentRecord;
    setLatestResult(result);
    setSelectedFile(null);
    await loadDocuments();
  }

  async function searchDocuments(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const trimmedQuery = query.trim();
    const url = trimmedQuery
      ? `${API_BASE_URL}/documents/search?q=${encodeURIComponent(trimmedQuery)}`
      : `${API_BASE_URL}/documents`;

    const response = await fetch(url);
    if (!response.ok) {
      setError(await getApiErrorMessage(response, "Search failed."));
      return;
    }
    setDocuments(await response.json());
  }

  return (
    <main className="page">
      <section className="header">
        <div>
          <p className="eyebrow">Local MVP</p>
          <h1>KlearIO</h1>
          <p className="intro">
            Upload a PDF, extract text, detect its type, propose a clear name,
            and keep it searchable locally.
          </p>
        </div>
      </section>

      <section className="panel-grid">
        <form className="panel" onSubmit={uploadDocument}>
          <h2>Upload PDF</h2>
          <input
            accept="application/pdf"
            type="file"
            onChange={(event) =>
              setSelectedFile(event.target.files?.item(0) ?? null)
            }
          />
          <button disabled={isUploading} type="submit">
            {isUploading ? "Processing..." : "Upload and process"}
          </button>
        </form>

        <form className="panel" onSubmit={searchDocuments}>
          <h2>Search</h2>
          <input
            placeholder="Search by issuer, type, text..."
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <div className="button-row">
            <button type="submit">Search</button>
            <button
              type="button"
              onClick={() => {
                setQuery("");
                void loadDocuments();
              }}
            >
              Reset
            </button>
          </div>
        </form>
      </section>

      {error ? <p className="error">{error}</p> : null}

      {latestResult ? (
        <section className="result">
          <div className="result-heading">
            <div>
              <p className="eyebrow">Processing result</p>
              <h2>Suggested classification</h2>
            </div>
            <span>{latestResult.status}</span>
          </div>
          <p className="result-note">
            KlearIO has proposed a file name and folder. The file has not been
            physically renamed or moved yet.
          </p>
          <DocumentDetails document={latestResult} />
        </section>
      ) : null}

      <section className="documents">
        <div className="section-heading">
          <h2>Documents</h2>
          <span>{visibleDocuments.length} saved</span>
        </div>
        <div className="document-list">
          {visibleDocuments.map((document) => (
            <article className="document-card" key={document.id}>
              <h3>{document.proposed_file_name}</h3>
              <DocumentDetails document={document} compact />
            </article>
          ))}
          {visibleDocuments.length === 0 ? (
            <p className="empty">No documents yet.</p>
          ) : null}
        </div>
      </section>
    </main>
  );
}

function DocumentDetails({
  document,
  compact = false,
}: {
  document: DocumentRecord;
  compact?: boolean;
}) {
  return (
    <dl className={compact ? "details compact" : "details"}>
      <div>
        <dt>Document type</dt>
        <dd>{formatValue(document.document_type)}</dd>
      </div>
      <div>
        <dt>Issuer</dt>
        <dd>{formatValue(document.issuer)}</dd>
      </div>
      <div>
        <dt>Document date</dt>
        <dd>{formatValue(document.document_date)}</dd>
      </div>
      <div>
        <dt>Amount</dt>
        <dd>{formatValue(document.amount)}</dd>
      </div>
      <div>
        <dt>Reference number</dt>
        <dd>{formatValue(document.reference_number)}</dd>
      </div>
      <div>
        <dt>Suggested file name</dt>
        <dd>{formatValue(document.proposed_file_name)}</dd>
      </div>
      <div>
        <dt>Suggested folder</dt>
        <dd>{formatValue(document.proposed_folder)}</dd>
      </div>
      <div>
        <dt>Status</dt>
        <dd>{formatValue(document.status)}</dd>
      </div>
    </dl>
  );
}

function formatValue(value: string | null) {
  return value?.trim() ? value : "Not detected";
}

async function getApiErrorMessage(response: Response, fallback: string) {
  try {
    const payload = await response.json();
    return payload?.detail?.error?.message ?? fallback;
  } catch {
    return fallback;
  }
}
