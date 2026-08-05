import { useState } from 'react'
import { uploadDocument } from '../../api/document'
import type { UploadDocumentResponse } from '../../types/document'

function DocumentUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadResult, setUploadResult] =
    useState<UploadDocumentResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [isUploading, setIsUploading] = useState(false)

  async function handleUpload() {
    if (!selectedFile) {
      setErrorMessage('请先选择一份履历文件')
      return
    }

    setIsUploading(true)
    setErrorMessage('')
    setUploadResult(null)

    try {
      const result = await uploadDocument(selectedFile)
      setUploadResult(result)
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : '文件上传失败，请稍后重试'

      setErrorMessage(message)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <section>
      <h2>上传履历</h2>

      <input
        type="file"
        accept=".pdf,.md,.jpg,.jpeg,.png,.docx"
        onChange={(event) => {
          const file = event.target.files?.[0] ?? null

          setSelectedFile(file)
          setErrorMessage('')
          setUploadResult(null)
        }}
      />

      <button
        type="button"
        disabled={!selectedFile || isUploading}
        onClick={handleUpload}
      >
        {isUploading ? '上传中...' : '上传文件'}
      </button>

      {selectedFile && (
        <p>已选择：{selectedFile.name}</p>
      )}

      {errorMessage && (
        <p>{errorMessage}</p>
      )}

      {uploadResult && (
        <div>
          <p>{uploadResult.message}</p>
          <p>文件名：{uploadResult.filename}</p>
          <p>文档 ID：{uploadResult.document_id}</p>
        </div>
      )}
    </section>
  )
}

export default DocumentUpload