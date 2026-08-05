interface ApiErrorResponse {
  detail?: string
}

export async function apiRequest<T>(
  url: string,
  options: RequestInit,
  defaultErrorMessage: string,
): Promise<T> {
  let response: Response

  try {
    response = await fetch(url, options)
  } catch {
    throw new Error('无法连接到服务器，请确认后端服务已启动')
  }

  if (!response.ok) {
    const errorData: ApiErrorResponse | null = await response
      .json()
      .catch(() => null)

    throw new Error(
      errorData?.detail ??
        `${defaultErrorMessage}（状态码：${response.status}）`,
    )
  }

  return (await response.json()) as T
}