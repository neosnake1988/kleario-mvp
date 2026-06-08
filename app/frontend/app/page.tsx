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

type MetadataForm = {
  document_type: string;
  issuer: string;
  document_date: string;
  amount: string;
  reference_number: string;
  proposed_file_name: string;
  proposed_folder: string;
  status: string;
};

type MetadataField = keyof MetadataForm;

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [latestResult, setLatestResult] = useState<DocumentRecord | null>(null);
  const [query, setQuery] = useState("");
  const [activeSearchQuery, setActiveSearchQuery] = useState("");
  const [documentTypeFilter, setDocumentTypeFilter] = useState("all");
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editingDocumentId, setEditingDocumentId] = useState<number | null>(
    null,
  );
  const [editForm, setEditForm] = useState<MetadataForm | null>(null);
  const [error, setError] = useState<string | null>(null);

  const documentTypeOptions = useMemo(
    () =>
      Array.from(
        new Set(
          documents
            .map((document) => document.document_type)
            .filter((documentType) => documentType.trim()),
        ),
      ).sort(),
    [documents],
  );

  const visibleDocuments = useMemo(() => {
    if (documentTypeFilter === "all") {
      return documents;
    }
    return documents.filter(
      (document) => document.document_type === documentTypeFilter,
    );
  }, [documentTypeFilter, documents]);

  const hasSearchOrFilter =
    activeSearchQuery.trim().length > 0 || documentTypeFilter !== "all";

  useEffect(() => {
    void loadDocuments();
  }, []);

  async function loadDocuments(searchQuery = activeSearchQuery) {
    setIsLoadingDocuments(true);
    setError(null);

    const trimmedQuery = searchQuery.trim();
    const url = trimmedQuery
      ? `${API_BASE_URL}/documents/search?q=${encodeURIComponent(trimmedQuery)}`
      : `${API_BASE_URL}/documents`;

    try {
      const response = await fetch(url);
      if (!response.ok) {
        setError(await getApiErrorMessage(response, "Unable to load documents."));
        return;
      }
      setDocuments(await response.json());
      setActiveSearchQuery(trimmedQuery);
    } catch {
      setError("Unable to load documents.");
    } finally {
      setIsLoadingDocuments(false);
    }
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
    await loadDocuments(activeSearchQuery);
  }

  async function searchDocuments(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadDocuments(query);
  }

  async function resetDocuments() {
    setQuery("");
    setDocumentTypeFilter("all");
    await loadDocuments("");
  }

  function startEditing(document: DocumentRecord) {
    setError(null);
    setEditingDocumentId(document.id);
    setEditForm(toEditForm(document));
  }

  function cancelEditing() {
    setEditingDocumentId(null);
    setEditForm(null);
    setIsSaving(false);
  }

  function updateEditField(field: MetadataField, value: string) {
    setEditForm((current) =>
      current ? { ...current, [field]: value } : current,
    );
  }

  async function saveMetadata(documentId: number) {
    if (!editForm) {
      return;
    }

    setIsSaving(true);
    setError(null);

    const response = await fetch(
      `${API_BASE_URL}/documents/${documentId}/metadata`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(toMetadataPayload(editForm)),
      },
    );

    setIsSaving(false);

    if (!response.ok) {
      setError(
        await getApiErrorMessage(response, "Metadata could not be saved."),
      );
      return;
    }

    const updatedDocument = (await response.json()) as DocumentRecord;
    setDocuments((current) =>
      current.map((document) =>
        document.id === updatedDocument.id ? updatedDocument : document,
      ),
    );
    setLatestResult((current) =>
      current?.id === updatedDocument.id ? updatedDocument : current,
    );
    cancelEditing();
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
        <UploadPanel
          isUploading={isUploading}
          onFileChange={setSelectedFile}
          onSubmit={uploadDocument}
        />
        <DocumentSearchControls
          documentTypeFilter={documentTypeFilter}
          documentTypeOptions={documentTypeOptions}
          onDocumentTypeFilterChange={setDocumentTypeFilter}
          onQueryChange={setQuery}
          onRefresh={() => void loadDocuments()}
          onReset={() => void resetDocuments()}
          onSearch={searchDocuments}
          query={query}
        />
      </section>

      {error ? <p className="error">{error}</p> : null}

      {latestResult ? (
        <LatestResultPanel
          document={latestResult}
          editForm={editForm}
          isEditing={editingDocumentId === latestResult.id}
          isSaving={isSaving}
          onCancel={cancelEditing}
          onChange={updateEditField}
          onEdit={() => startEditing(latestResult)}
          onSave={() => void saveMetadata(latestResult.id)}
        />
      ) : null}

      <section className="documents">
        <div className="section-heading">
          <h2>Documents</h2>
          <span>{documents.length} saved</span>
        </div>
        {activeSearchQuery ? (
          <p className="list-context">Search results for "{activeSearchQuery}"</p>
        ) : null}
        <div className="document-list">
          {isLoadingDocuments ? (
            <p className="empty">Loading documents...</p>
          ) : (
            visibleDocuments.map((document) => (
              <DocumentCard
                document={document}
                editForm={editForm}
                isEditing={
                  editingDocumentId === document.id &&
                  latestResult?.id !== document.id
                }
                isSaving={isSaving}
                key={document.id}
                onCancel={cancelEditing}
                onChange={updateEditField}
                onEdit={() => startEditing(document)}
                onSave={() => void saveMetadata(document.id)}
              />
            ))
          )}
          {!isLoadingDocuments && visibleDocuments.length === 0 ? (
            <p className="empty">
              {hasSearchOrFilter
                ? "No documents match this search."
                : "No documents yet."}
            </p>
          ) : null}
        </div>
      </section>
    </main>
  );
}

function UploadPanel({
  isUploading,
  onFileChange,
  onSubmit,
}: {
  isUploading: boolean;
  onFileChange: (file: File | null) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="panel" onSubmit={onSubmit}>
      <h2>Upload PDF</h2>
      <input
        accept="application/pdf"
        type="file"
        onChange={(event) => onFileChange(event.target.files?.item(0) ?? null)}
      />
      <button disabled={isUploading} type="submit">
        {isUploading ? "Processing..." : "Upload and process"}
      </button>
    </form>
  );
}

function DocumentSearchControls({
  documentTypeFilter,
  documentTypeOptions,
  onDocumentTypeFilterChange,
  onQueryChange,
  onRefresh,
  onReset,
  onSearch,
  query,
}: {
  documentTypeFilter: string;
  documentTypeOptions: string[];
  onDocumentTypeFilterChange: (value: string) => void;
  onQueryChange: (value: string) => void;
  onRefresh: () => void;
  onReset: () => void;
  onSearch: (event: FormEvent<HTMLFormElement>) => void;
  query: string;
}) {
  return (
    <form className="panel" onSubmit={onSearch}>
      <h2>Find documents</h2>
      <label className="search-field">
        <span>Search</span>
        <input
          placeholder="Issuer, type, reference, folder..."
          type="search"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
        />
      </label>
      <label className="search-field">
        <span>Document type</span>
        <select
          value={documentTypeFilter}
          onChange={(event) => onDocumentTypeFilterChange(event.target.value)}
        >
          <option value="all">All types</option>
          {documentTypeOptions.map((documentType) => (
            <option key={documentType} value={documentType}>
              {documentType}
            </option>
          ))}
        </select>
      </label>
      <div className="button-row">
        <button type="submit">Search</button>
        <button type="button" onClick={onReset}>
          Reset
        </button>
        <button type="button" onClick={onRefresh}>
          Refresh
        </button>
      </div>
    </form>
  );
}

function LatestResultPanel({
  document,
  editForm,
  isEditing,
  isSaving,
  onCancel,
  onChange,
  onEdit,
  onSave,
}: {
  document: DocumentRecord;
  editForm: MetadataForm | null;
  isEditing: boolean;
  isSaving: boolean;
  onCancel: () => void;
  onChange: (field: MetadataField, value: string) => void;
  onEdit: () => void;
  onSave: () => void;
}) {
  return (
    <section className="result">
      <div className="result-heading">
        <div>
          <p className="eyebrow">Processing result</p>
          <h2>Suggested classification</h2>
        </div>
        <span>{document.status}</span>
      </div>
      <p className="result-note">
        KlearIO has proposed a file name and folder. The file has not been
        physically renamed or moved yet.
      </p>
      {isEditing && editForm ? (
        <MetadataEditForm
          form={editForm}
          isSaving={isSaving}
          onCancel={onCancel}
          onChange={onChange}
          onSave={onSave}
        />
      ) : (
        <>
          <DocumentDetails document={document} />
          <DocumentActions document={document} onEdit={onEdit} />
        </>
      )}
    </section>
  );
}

function DocumentCard({
  document,
  editForm,
  isEditing,
  isSaving,
  onCancel,
  onChange,
  onEdit,
  onSave,
}: {
  document: DocumentRecord;
  editForm: MetadataForm | null;
  isEditing: boolean;
  isSaving: boolean;
  onCancel: () => void;
  onChange: (field: MetadataField, value: string) => void;
  onEdit: () => void;
  onSave: () => void;
}) {
  return (
    <article className="document-card">
      <div className="document-card-heading">
        <h3>{document.proposed_file_name}</h3>
        <span>{formatValue(document.document_type)}</span>
      </div>
      {isEditing && editForm ? (
        <MetadataEditForm
          form={editForm}
          isSaving={isSaving}
          onCancel={onCancel}
          onChange={onChange}
          onSave={onSave}
        />
      ) : (
        <>
          <DocumentDetails document={document} compact />
          <DocumentActions document={document} onEdit={onEdit} />
        </>
      )}
    </article>
  );
}

function DocumentActions({
  document,
  onEdit,
}: {
  document: DocumentRecord;
  onEdit: () => void;
}) {
  return (
    <div className="metadata-actions">
      <a href={originalDocumentUrl(document)} rel="noreferrer" target="_blank">
        Open original document
      </a>
      <button type="button" onClick={onEdit}>
        Edit
      </button>
    </div>
  );
}

function MetadataEditForm({
  form,
  isSaving,
  onCancel,
  onChange,
  onSave,
}: {
  form: MetadataForm;
  isSaving: boolean;
  onCancel: () => void;
  onChange: (field: MetadataField, value: string) => void;
  onSave: () => void;
}) {
  return (
    <form
      className="metadata-form"
      onSubmit={(event) => {
        event.preventDefault();
        onSave();
      }}
    >
      <MetadataInput
        field="document_type"
        label="Document type"
        value={form.document_type}
        onChange={onChange}
      />
      <MetadataInput
        field="issuer"
        label="Issuer"
        value={form.issuer}
        onChange={onChange}
      />
      <MetadataInput
        field="document_date"
        label="Document date"
        value={form.document_date}
        onChange={onChange}
      />
      <MetadataInput
        field="amount"
        label="Amount"
        value={form.amount}
        onChange={onChange}
      />
      <MetadataInput
        field="reference_number"
        label="Reference number"
        value={form.reference_number}
        onChange={onChange}
      />
      <MetadataInput
        field="proposed_file_name"
        label="Suggested file name"
        value={form.proposed_file_name}
        onChange={onChange}
      />
      <MetadataInput
        field="proposed_folder"
        label="Suggested folder"
        value={form.proposed_folder}
        onChange={onChange}
      />
      <MetadataInput
        field="status"
        label="Status"
        value={form.status}
        onChange={onChange}
      />
      <div className="metadata-actions">
        <button disabled={isSaving} type="submit">
          {isSaving ? "Saving..." : "Save"}
        </button>
        <button disabled={isSaving} type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}

function MetadataInput({
  field,
  label,
  value,
  onChange,
}: {
  field: MetadataField;
  label: string;
  value: string;
  onChange: (field: MetadataField, value: string) => void;
}) {
  return (
    <label>
      <span>{label}</span>
      <input
        value={value}
        onChange={(event) => onChange(field, event.target.value)}
      />
    </label>
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

function toEditForm(document: DocumentRecord): MetadataForm {
  return {
    document_type: document.document_type,
    issuer: document.issuer ?? "",
    document_date: document.document_date ?? "",
    amount: document.amount ?? "",
    reference_number: document.reference_number ?? "",
    proposed_file_name: document.proposed_file_name,
    proposed_folder: document.proposed_folder,
    status: document.status,
  };
}

function toMetadataPayload(form: MetadataForm) {
  return {
    document_type: form.document_type.trim(),
    issuer: optionalValue(form.issuer),
    document_date: optionalValue(form.document_date),
    amount: optionalValue(form.amount),
    reference_number: optionalValue(form.reference_number),
    proposed_file_name: form.proposed_file_name.trim(),
    proposed_folder: form.proposed_folder.trim(),
    status: form.status.trim(),
  };
}

function optionalValue(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function originalDocumentUrl(document: DocumentRecord) {
  return `${API_BASE_URL}/documents/${document.id}/file`;
}

async function getApiErrorMessage(response: Response, fallback: string) {
  try {
    const payload = await response.json();
    return payload?.detail?.error?.message ?? fallback;
  } catch {
    return fallback;
  }
}
