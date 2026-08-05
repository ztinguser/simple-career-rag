export type WorkflowStep =
  | 'upload'
  | 'parse'
  | 'chunk'
  | 'index'

export type WorkflowStatus =
  | 'idle'
  | 'running'
  | 'success'
  | 'error'

export interface WorkflowState {
  currentStep: WorkflowStep | null
  status: WorkflowStatus
  documentId: string | null
  errorMessage: string
  indexedChunkCount: number | null
}

type WorkflowAction =
  | { type: 'START_WORKFLOW' }
  | { type: 'START_STEP'; step: WorkflowStep }
  | { type: 'SAVE_DOCUMENT_ID'; documentId: string }
  | { type: 'COMPLETE_WORKFLOW'; indexedChunkCount: number }
  | { type: 'FAIL_WORKFLOW'; errorMessage: string }
  | { type: 'RESET_WORKFLOW' }

export const initialWorkflowState: WorkflowState = {
  currentStep: null,
  status: 'idle',
  documentId: null,
  errorMessage: '',
  indexedChunkCount: null,
}

export function workflowReducer(
  state: WorkflowState,
  action: WorkflowAction,
): WorkflowState {
  switch (action.type) {
    case 'START_WORKFLOW':
      return {
        ...initialWorkflowState,
        currentStep: 'upload',
        status: 'running',
      }

    case 'START_STEP':
      return {
        ...state,
        currentStep: action.step,
        status: 'running',
        errorMessage: '',
      }

    case 'SAVE_DOCUMENT_ID':
      return {
        ...state,
        documentId: action.documentId,
      }

    case 'COMPLETE_WORKFLOW':
      return {
        ...state,
        currentStep: 'index',
        status: 'success',
        indexedChunkCount: action.indexedChunkCount,
      }

    case 'FAIL_WORKFLOW':
      return {
        ...state,
        status: 'error',
        errorMessage: action.errorMessage,
      }

    case 'RESET_WORKFLOW':
      return initialWorkflowState

    default:
      return state
  }
}