import type {
  ChunkDocumentResponse,
  ParseDocumentResponse,
  UploadDocumentResponse } from '../types/document'

export async function uploadDocument(
  file: File,
): Promise<UploadDocumentResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('/api/documents/upload', {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const errorData: { detail?: string } | null = await response
      .json()
      .catch(() => null)

    throw new Error(
      errorData?.detail ?? `文件上传失败（状态码：${response.status}）`,
    )
  }

  const data = (await response.json()) as UploadDocumentResponse

  return data
}

export async function parseDocument(
  documentId: string,
): Promise<ParseDocumentResponse> {
  const response = await fetch(
    `/api/documents/parse/${documentId}`,
    {
      method: 'POST',
    },
  )

  if (!response.ok) {
    const errorData: { detail?: string } | null = await response
      .json()
      .catch(() => null)

    throw new Error(
      errorData?.detail ?? `文档解析失败（状态码：${response.status}）`,
    )
  }

  const data = (await response.json()) as ParseDocumentResponse

  return data
}

export async function chunkDocument(
  documentId: string,
): Promise<ChunkDocumentResponse> {
  const response = await fetch(
    `/api/documents/chunk/${documentId}`,
    {
      method: 'POST',
    },
  )

  if (!response.ok) {
    const errorData: { detail?: string } | null = await response
      .json()
      .catch(() => null)

    throw new Error(
      errorData?.detail ?? `文档分块失败（状态码：${response.status}）`,
    )
  }

  const data = (await response.json()) as ChunkDocumentResponse

  return data
}