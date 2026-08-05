import {apiRequest} from './http'
import type {
    ChunkDocumentResponse,
    ParseDocumentResponse,
    UploadDocumentResponse,
} from '../types/document'

export function uploadDocument(
    file: File,
): Promise<UploadDocumentResponse> {
    const formData = new FormData()
    formData.append('file', file)

    return apiRequest<UploadDocumentResponse>(
        '/api/documents/upload',
        {
            method: 'POST',
            body: formData,
        },
        '文件上传失败',
    )
}

export function parseDocument(
    documentId: string,
): Promise<ParseDocumentResponse> {
    return apiRequest<ParseDocumentResponse>(
        `/api/documents/parse/${documentId}`,
        {
            method: 'POST',
        },
        '文档解析失败',
    )
}

export function chunkDocument(
    documentId: string,
): Promise<ChunkDocumentResponse> {
    return apiRequest<ChunkDocumentResponse>(
        `/api/documents/chunk/${documentId}`,
        {
            method: 'POST',
        },
        '文档分块失败',
    )
}