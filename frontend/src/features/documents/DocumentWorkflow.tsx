import {useState} from 'react'
import {
    chunkDocument, indexDocument,
    parseDocument,
    uploadDocument,
} from '../../api/document'
import type {
    ChunkDocumentResponse, IndexDocumentResponse,
    ParseDocumentResponse,
    UploadDocumentResponse,
} from '../../types/document'

function DocumentWorkflow() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [uploadResult, setUploadResult] = useState<UploadDocumentResponse | null>(null)
    const [parseResult, setParseResult] = useState<ParseDocumentResponse | null>(null)
    const [chunkResult, setChunkResult] = useState<ChunkDocumentResponse | null>(null)
    const [indexResult, setIndexResult] = useState<IndexDocumentResponse | null>(null)

    const [errorMessage, setErrorMessage] = useState('')
    const [isUploading, setIsUploading] = useState(false)
    const [isParsing, setIsParsing] = useState(false)
    const [isChunking, setIsChunking] = useState(false)
    const [isIndexing, setIsIndexing] = useState(false)

    async function handleUpload() {
        if (!selectedFile) {
            setErrorMessage('请先选择一份履历文件')
            return
        }

        setIsUploading(true)
        setErrorMessage('')
        setUploadResult(null)
        setParseResult(null)
        setChunkResult(null)
        setIndexResult(null)

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
        setChunkResult(null)
        setIndexResult(null)

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

    async function handleChunk() {
        if (!parseResult) {
            setErrorMessage('请先解析履历文件')
            return
        }

        setIsChunking(true)
        setErrorMessage('')
        setChunkResult(null)
        setIndexResult(null)

        try {
            const result = await chunkDocument(parseResult.document_id)
            setChunkResult(result)
        } catch (error) {
            const message =
                error instanceof Error
                    ? error.message
                    : '文档分块失败，请稍后重试'

            setErrorMessage(message)
        } finally {
            setIsChunking(false)
        }
    }

    async function handleIndex() {
        if (!chunkResult) {
            setErrorMessage('请先生成文档分块')
            return
        }

        setIsIndexing(true)
        setErrorMessage('')
        setIndexResult(null)

        try {
            const result = await indexDocument(chunkResult.document_id)
            setIndexResult(result)
        } catch (error) {
            const message =
                error instanceof Error
                    ? error.message
                    : '文档索引失败，请稍后重试'

            setErrorMessage(message)
        } finally {
            setIsIndexing(false)
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
                    setChunkResult(null)
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
                    <button
                        type="button"
                        disabled={isChunking}
                        onClick={handleChunk}
                    >
                        {isChunking ? '分块中...' : '生成文档分块'}
                    </button>
                </div>
            )}

            {chunkResult && (
                <div>
                    <p>{chunkResult.message}</p>
                    <p>分块数量：{chunkResult.chunk_count}</p>

                    <h3>分块预览</h3>

                    {chunkResult.chunks_preview.map((chunk) => (
                        <article key={chunk.chunk_id}>
                            <h4>
                                {chunk.headings.join(' > ') || '无标题'}
                            </h4>

                            <p>
                                页码：{chunk.page_numbers.join(', ') || '未知'}
                            </p>

                            <p>{chunk.content}</p>
                        </article>
                    ))}

                    <button
                        type="button"
                        disabled={isIndexing}
                        onClick={handleIndex}
                    >
                        {isIndexing ? '索引中...' : '写入向量数据库'}
                    </button>

                </div>
            )}

            {indexResult && (
                <div>
                    <p>{indexResult.message}</p>
                    <p>文件名：{indexResult.filename}</p>
                    <p>已索引分块数：{indexResult.chunk_count}</p>
                    <p>履历资料准备完成，可以开始问答。</p>
                </div>
            )}
        </section>
    )
}

export default DocumentWorkflow