import {useState} from 'react'
import type {FormEvent} from 'react'
import {FiArrowUp} from 'react-icons/fi'

import {askQuestion} from '../../api/chat'
import type {RAGAnswer} from '../../types/chat'

interface ChatRecord {
    id: string
    result: RAGAnswer
}

interface UserMessageProps {
    children: string
}

function UserMessage({children}: UserMessageProps) {
    return (
        <div className="flex justify-end">
            <p className="max-w-xs rounded-2xl rounded-tr-lg bg-zinc-700 px-4 py-2 text-sm leading-relaxed text-white shadow-sm sm:max-w-lg sm:px-6 sm:py-3 sm:text-base lg:max-w-2xl lg:px-8 lg:py-4">
                {children}
            </p>
        </div>
    )
}

interface AssistantMessageProps {
    result?: RAGAnswer
    isLoading?: boolean
}

function AssistantMessage({result, isLoading = false}: AssistantMessageProps) {
    return (
        <div className="flex items-start gap-3 sm:gap-4 lg:gap-6">
            <img
                src="/human.png"
                alt="AI 履历助手头像"
                className="size-14 shrink-0 rounded-full border-2 border-white object-cover shadow-lg sm:size-16 lg:size-24 lg:border-4"
            />

            <div className="min-w-0 flex-1 rounded-2xl rounded-tl-lg bg-white px-4 py-3 shadow-sm sm:px-6 lg:max-w-3xl lg:px-8 lg:py-2">
                <p className="whitespace-pre-wrap text-sm leading-relaxed sm:text-base">
                    {isLoading ? '正在思考...' : result?.answer}
                </p>

                {result?.rewritten_question && (
                    <p className="mt-4 text-sm leading-relaxed text-zinc-500">
                        改写问题：{result.rewritten_question}
                    </p>
                )}

                {result && result.citations.length > 0 && (
                    <details className="mt-1 text-xs text-zinc-600">
                        <summary className="cursor-pointer leading-none text-zinc-800">
                            查看原文引用
                        </summary>

                        <ol className="mt-3 space-y-4">
                            {result.citations.map((citation) => (
                                <li
                                    key={citation.citation_id}
                                    className="rounded-2xl bg-zinc-100 p-4"
                                >
                                    <p className="text-zinc-800">
                                        [{citation.citation_id}] {citation.source_name}
                                    </p>
                                    <p className="mt-1">
                                        页码：{citation.page_numbers.join(', ') || '未知'}
                                    </p>
                                    <blockquote className="mt-2 leading-relaxed">
                                        {citation.content}
                                    </blockquote>
                                </li>
                            ))}
                        </ol>
                    </details>
                )}
            </div>
        </div>
    )
}

function ChatPanel() {
    const [question, setQuestion] = useState('')
    const [records, setRecords] = useState<ChatRecord[]>([])
    const [pendingQuestion, setPendingQuestion] = useState('')
    const [errorMessage, setErrorMessage] = useState('')
    const [isAsking, setIsAsking] = useState(false)

    const hasConversation = records.length > 0 || Boolean(pendingQuestion)

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
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
        setPendingQuestion(normalizedQuestion)
        setQuestion('')
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
        } catch (error) {
            const message =
                error instanceof Error
                    ? error.message
                    : '履历问答失败，请稍后重试'

            setErrorMessage(message)
            setQuestion(normalizedQuestion)
        } finally {
            setPendingQuestion('')
            setIsAsking(false)
        }
    }

    return (
        <main className="relative min-h-dvh overflow-hidden bg-white bg-[url('/background-img.png')] bg-cover bg-center font-sans text-black">
            {!hasConversation ? (
                <section className="relative flex h-dvh flex-col items-center overflow-y-auto px-5 pt-32 pb-36 sm:block sm:p-0">
                    <img
                        src="/human.png"
                        alt="AI 履历助手头像"
                        className="size-24 shrink-0 rounded-full border-4 border-white object-cover shadow-xl sm:absolute sm:top-1/4 sm:left-1/2 sm:size-28 sm:-translate-x-1/2"
                    />

                    <h1 className="mt-12 text-center text-2xl leading-tight font-bold sm:absolute sm:top-1/2 sm:left-1/2 sm:mt-0 sm:w-full sm:-translate-x-1/2 sm:px-5 sm:text-3xl lg:text-4xl">
                        Hello! 这是我的小蜜
                    </h1>
                </section>
            ) : (
                <section
                    aria-label="问答记录"
                    className="h-dvh overflow-y-auto px-4 pt-16 pb-36 sm:px-8 sm:pt-24 sm:pb-44 lg:px-16 lg:pt-32 lg:pb-52"
                >
                    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 sm:gap-10 lg:gap-12">
                        {records.map((record) => (
                            <article key={record.id} className="flex flex-col gap-7 sm:gap-9 lg:gap-12">
                                <UserMessage>{record.result.question}</UserMessage>
                                <AssistantMessage result={record.result}/>
                            </article>
                        ))}

                        {pendingQuestion && (
                            <div className="flex flex-col gap-7 sm:gap-9 lg:gap-12">
                                <UserMessage>{pendingQuestion}</UserMessage>
                                <AssistantMessage isLoading/>
                            </div>
                        )}
                    </div>
                </section>
            )}

            <div className="absolute inset-x-0 bottom-4 z-20 mx-auto w-full max-w-5xl px-4 sm:bottom-8 sm:px-8 lg:bottom-10">
                {errorMessage && (
                    <p
                        role="alert"
                        className="mb-3 rounded-2xl bg-red-50 px-5 py-3 text-sm font-medium text-red-700 shadow-sm"
                    >
                        {errorMessage}
                    </p>
                )}

                <form
                    onSubmit={handleSubmit}
                    className="flex h-12 items-center rounded-full bg-blue-100/60 py-2 pr-2 pl-4 shadow-xl backdrop-blur-xl sm:h-15 sm:py-2.5 sm:pr-2.5 sm:pl-6 lg:h-16 lg:py-2 lg:pr-2 lg:pl-8"
                >
                    <label htmlFor="question" className="sr-only">
                        输入问题
                    </label>
                    <input
                        id="question"
                        type="text"
                        value={question}
                        maxLength={500}
                        autoComplete="off"
                        disabled={isAsking}
                        placeholder="想要了解什么呢"
                        className="min-w-0 flex-1 appearance-none bg-transparent pr-3 text-base font-normal text-blue-800 outline-none placeholder:text-blue-800 focus:bg-transparent autofill:bg-transparent disabled:cursor-wait sm:pr-5"
                        onChange={(event) => {
                            setQuestion(event.target.value)
                            setErrorMessage('')
                        }}
                    />

                    <button
                        type="submit"
                        aria-label={isAsking ? '回答生成中' : '发送问题'}
                        disabled={!question.trim() || isAsking}
                        className="flex size-8 shrink-0 items-center justify-center rounded-full bg-zinc-900 text-white transition hover:bg-zinc-700 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-zinc-900 disabled:cursor-not-allowed sm:size-10 lg:size-12"
                    >
                        <FiArrowUp aria-hidden="true" className="size-4 sm:size-5 lg:size-6"/>
                    </button>
                </form>
            </div>
        </main>
    )
}

export default ChatPanel
