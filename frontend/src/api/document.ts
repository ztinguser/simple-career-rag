import type { UploadDocumentResponse } from '../types/document'

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