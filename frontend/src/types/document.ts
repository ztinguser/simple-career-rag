// 上传文档后的响应
export interface UploadDocumentResponse {
    document_id: string
    filename: string
    size_bytes: number
    message: string
}

// 解析文档后的响应
export interface ParseDocumentResponse {
    document_id: string
    filename: string
    page_count: number
    character_count: number
    markdown_preview: string
    message: string
}

// 文档切分后的一段原文
export interface DocumentChunk {
    chunk_id: string
    document_id: string
    source_name: string
    page_numbers: number[]
    headings: string[]
    content: string
    embedding_text: string
}

// 文档分块后的响应
export interface ChunkDocumentResponse {
    document_id: string
    filename: string
    chunk_count: number
    chunks_preview: DocumentChunk[]
    message: string
}

// 文档写入向量数据库后的响应
export interface IndexDocumentResponse {
    document_id: string
    filename: string
    chunk_count: number
    message: string
}