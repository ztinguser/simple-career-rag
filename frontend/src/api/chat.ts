import {apiRequest} from './http'
import type {
    AskQuestionRequest,
    RAGAnswer,
} from '../types/chat'

export function askQuestion(
    question: string,
): Promise<RAGAnswer> {
    const requestBody: AskQuestionRequest = {
        question,
    }

    return apiRequest<RAGAnswer>(
        '/api/chat/ask',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        },
        '履历问答失败',
    )
}