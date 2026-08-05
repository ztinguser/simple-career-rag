import {useState} from 'react'
import type {FormEvent} from 'react'
import {askQuestion} from '../../api/chat'
import type {RAGAnswer} from '../../types/chat'

interface ChatRecord {
    id: string
    result: RAGAnswer
}

function ChatPanel() {
    const [question, setQuestion] = useState('')
    const [records, setRecords] = useState<ChatRecord[]>([])
    const [errorMessage, setErrorMessage] = useState('')
    const [isAsking, setIsAsking] = useState(false)

    async function handleSubmit(
        event: FormEvent<HTMLFormElement>,
    ) {
        event.preventDefault()

        const normalizedQuestion = question.trim()

        if (!normalizedQuestion) {
            setErrorMessage('请输入需要询问的问题')
            return
        }

        if (normalizedQuestion.length > 500) {
            setErrorMessage('问题不能超过 500 个字符')
            return
        }

        setIsAsking(true)
        setErrorMessage('')

        try {
            const result = await askQuestion(normalizedQuestion)

            setRecords((currentRecords) => [
                ...currentRecords,
                {
                    id: crypto.randomUUID(),
                    result,
                },
            ])

            setQuestion('')
        } catch (error) {
            const message =
                error instanceof Error
                    ? error.message
                    : '履历问答失败，请稍后重试'

            setErrorMessage(message)
        } finally {
            setIsAsking(false)
        }
    }

    return (
        <section>
            <h2>履历问答</h2>

            <form onSubmit={handleSubmit}>
                <label htmlFor="question">
                    想了解候选人的什么信息？
                </label>

                <textarea
                    id="question"
                    value={question}
                    maxLength={500}
                    disabled={isAsking}
                    onChange={(event) => {
                        setQuestion(event.target.value)
                        setErrorMessage('')
                    }}
                />

                <button
                    type="submit"
                    disabled={!question.trim() || isAsking}
                >
                    {isAsking ? '回答生成中...' : '发送问题'}
                </button>
            </form>

            {errorMessage && (
                <p>{errorMessage}</p>
            )}

            <div aria-label="问答记录">
                {records.map((record) => (
                    <article key={record.id}>
                        <h3>问题</h3>
                        <p>{record.result.question}</p>

                        {record.result.rewritten_question && (
                            <>
                                <h3>问题改写</h3>
                                <p>{record.result.rewritten_question}</p>
                            </>
                        )}

                        <h3>回答</h3>
                        <p>{record.result.answer}</p>

                        {record.result.citations.length > 0 && (
                            <details>
                                <summary>
                                    查看原文引用
                                </summary>

                                <ol>
                                    {record.result.citations.map((citation) => (
                                        <li key={citation.citation_id}>
                                            <p>
                                                来源：{citation.source_name}
                                            </p>

                                            <p>
                                                页码：
                                                {citation.page_numbers.join(', ') || '未知'}
                                            </p>

                                            <p>
                                                标题：
                                                {citation.headings.join(' > ') || '无标题'}
                                            </p>

                                            <blockquote>
                                                {citation.content}
                                            </blockquote>
                                        </li>
                                    ))}
                                </ol>
                            </details>
                        )}
                    </article>
                ))}
            </div>
        </section>
    )
}

export default ChatPanel