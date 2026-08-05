// 向后端提交的问题
export interface AskQuestionRequest {
    question: string
}

// 回答引用的一段履历原文
export interface Citation {
    citation_id: number
    chunk_id: string
    source_name: string
    page_numbers: number[]
    headings: string[]
    content: string
}

// 一次完整的履历问答结果
export interface RAGAnswer {
    question: string
    answer: string
    citations: Citation[]
    rewritten_question: string | null
}