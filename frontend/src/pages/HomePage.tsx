import DocumentWorkflow from "../features/documents/DocumentWorkflow.tsx";
import ChatPanel from "../features/chat/ChatPanel.tsx";

function HomePage() {
    return (
        <main className="p-8">
            <h1 className="text-3xl font-bold">
                个人履历助手
            </h1>

            <p className="mt-4 text-gray-600">
                前端项目已成功启动。
            </p>

            {/*<DocumentWorkflow/>*/}
            <ChatPanel/>


        </main>
    )
}

export default HomePage