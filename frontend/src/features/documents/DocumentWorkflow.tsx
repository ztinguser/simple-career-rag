import { useState } from 'react'
import {
  parseDocument,
  uploadDocument,
} from '../../api/document'
import type {
  ParseDocumentResponse,
  UploadDocumentResponse,
} from '../../types/document'

function DocumentWorkflow() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadResult, setUploadResult] =
    useState<UploadDocumentResponse | null>(null)
  const [parseResult, setParseResult] =
    useState<ParseDocumentResponse | null>(null)

  const [errorMessage, setErrorMessage] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [isParsing, setIsParsing] = useState(false)

  async function handleUpload() {
    if (!selectedFile) {
      setErrorMessage('请先选择一份履历文件')
      return
    }

    setIsUploading(true)
    setErrorMessage('')
    setUploadResult(null)
    setParseResult(null)

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

  async function handleParse() {
    if (!uploadResult) {
      setErrorMessage('请先上传履历文件')
      return
    }

    setIsParsing(true)
    setErrorMessage('')
    setParseResult(null)

    try {
      const result = await parseDocument(uploadResult.document_id)
      setParseResult(result)
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : '文档解析失败，请稍后重试'

      setErrorMessage(message)
    } finally {
      setIsParsing(false)
    }
  }

  return (
    <section>
      <h2>准备履历资料</h2>

      <input
        type="file"
        accept=".pdf,.md,.jpg,.jpeg,.png,.docx"
        onChange={(event) => {
          const file = event.target.files?.[0] ?? null

          setSelectedFile(file)
          setUploadResult(null)
          setParseResult(null)
          setErrorMessage('')
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

          <button
            type="button"
            disabled={isParsing}
            onClick={handleParse}
          >
            {isParsing ? '解析中...' : '解析文档'}
          </button>
        </div>
      )}

      {parseResult && (
        <div>
          <p>{parseResult.message}</p>
          <p>页数：{parseResult.page_count}</p>
          <p>字符数：{parseResult.character_count}</p>

          <h3>解析内容预览</h3>
          <pre>{parseResult.markdown_preview}</pre>
        </div>
      )}
    </section>
  )
}

export default DocumentWorkflow