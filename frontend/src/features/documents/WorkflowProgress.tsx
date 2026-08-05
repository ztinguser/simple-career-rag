import type {
    WorkflowStatus,
    WorkflowStep,
} from './workflowReducer'

type StepStatus = 'pending' | 'running' | 'success' | 'error'

interface WorkflowProgressProps {
    currentStep: WorkflowStep | null
    workflowStatus: WorkflowStatus
}

const WORKFLOW_STEPS: Array<{
    key: WorkflowStep
    label: string
}> = [
    {key: 'upload', label: '上传文件'},
    {key: 'parse', label: '解析文档'},
    {key: 'chunk', label: '文档分片'},
    {key: 'index', label: '向量入库'},
]

const STATUS_LABELS: Record<StepStatus, string> = {
    pending: '等待中',
    running: '进行中',
    success: '已完成',
    error: '失败',
}

function getStepStatus(
    step: WorkflowStep,
    currentStep: WorkflowStep | null,
    workflowStatus: WorkflowStatus,
): StepStatus {
    if (!currentStep) {
        return 'pending'
    }

    // 整个流程完成时，所有节点都显示为完成
    if (workflowStatus === 'success') {
        return 'success'
    }

    const stepIndex = WORKFLOW_STEPS.findIndex((item) => item.key === step)
    const currentIndex = WORKFLOW_STEPS.findIndex(
        (item) => item.key === currentStep,
    )

    if (stepIndex < currentIndex) {
        return 'success'
    }

    if (stepIndex > currentIndex) {
        return 'pending'
    }

    return workflowStatus === 'error' ? 'error' : 'running'
}

function WorkflowProgress({
                              currentStep,
                              workflowStatus,
                          }: WorkflowProgressProps) {
    return (
        <ol aria-label="履历处理进度">
            {WORKFLOW_STEPS.map((step) => {
                const stepStatus = getStepStatus(
                    step.key,
                    currentStep,
                    workflowStatus,
                )

                return (
                    <li
                        key={step.key}
                        data-status={stepStatus}
                        aria-current={stepStatus === 'running' ? 'step' : undefined}
                    >
                        <span>{step.label}</span>
                        <span>：{STATUS_LABELS[stepStatus]}</span>
                    </li>
                )
            })}
        </ol>
    )
}

export default WorkflowProgress
