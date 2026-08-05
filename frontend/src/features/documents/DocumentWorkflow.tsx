import { useReducer, useState } from 'react'
import {
  chunkDocument,
  indexDocument,
  parseDocument,
  uploadDocument,
} from '../../api/document'
import {
  initialWorkflowState,
  workflowReducer,
} from './workflowReducer'
import WorkflowProgress from './WorkflowProgress'

function DocumentWorkflow() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [workflow, dispatch] = useReducer(
    workflowReducer,
    initialWorkflowState,
  )

  const isRunning = workflow.status === 'running'

  async function handleProcess() {
    if (!selectedFile) {
      dispatch({
        type: 'FAIL_WORKFLOW',
        errorMessage: '请先选择一份履历文件',
      })
      return
    }

    dispatch({ type: 'START_WORKFLOW' })

    try {
      // 第一步：上传文件并取得后端生成的文档 ID
      const uploadResult = await uploadDocument(selectedFile)

      dispatch({
        type: 'SAVE_DOCUMENT_ID',
        documentId: uploadResult.document_id,
      })

      // 第二步：将原始文件解析为 Markdown
      dispatch({ type: 'START_STEP', step: 'parse' })
      await parseDocument(uploadResult.document_id)

      // 第三步：将解析结果切分成可以检索的文本块
      dispatch({ type: 'START_STEP', step: 'chunk' })
      await chunkDocument(uploadResult.document_id)

      // 第四步：生成向量并写入 Qdrant
      dispatch({ type: 'START_STEP', step: 'index' })
      const indexResult = await indexDocument(uploadResult.document_id)

      dispatch({
        type: 'COMPLETE_WORKFLOW',
        indexedChunkCount: indexResult.chunk_count,
      })
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : '履历处理失败，请稍后重试'

      dispatch({
        type: 'FAIL_WORKFLOW',
        errorMessage: message,
      })
    }
  }

  return (
    <section>
      <h2>准备履历资料</h2>

      <input
        type="file"
        accept=".pdf,.md,.jpg,.jpeg,.png,.docx"
        disabled={isRunning}
        onChange={(event) => {
          const file = event.target.files?.[0] ?? null

          setSelectedFile(file)
          dispatch({ type: 'RESET_WORKFLOW' })
        }}
      />

      <button
        type="button"
        disabled={!selectedFile || isRunning}
        onClick={handleProcess}
      >
        {isRunning ? '处理中...' : '开始处理'}
      </button>

      {selectedFile && <p>已选择：{selectedFile.name}</p>}

      <WorkflowProgress
        currentStep={workflow.currentStep}
        workflowStatus={workflow.status}
      />

      {workflow.status === 'error' && <p>{workflow.errorMessage}</p>}

      {workflow.status === 'success' && (
        <div>
          <p>履历资料准备完成，可以开始问答。</p>
          <p>文档 ID：{workflow.documentId}</p>
          <p>已索引分块数：{workflow.indexedChunkCount}</p>
        </div>
      )}
    </section>
  )
}

export default DocumentWorkflow
