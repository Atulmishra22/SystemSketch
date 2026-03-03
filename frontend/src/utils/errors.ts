/**
 * Parses API error responses into a human-readable string.
 *
 * FastAPI can return two formats:
 *  - Simple string:  { detail: "Incorrect username or password" }
 *  - Pydantic 422:   { detail: [{ loc: [...], msg: "Value error, ..." }] }
 */
export function parseApiError(err: unknown, fallback = 'Something went wrong'): string {
  const e = err as { response?: { data?: { detail?: unknown } } }
  const detail = e?.response?.data?.detail

  if (!detail) return fallback

  // Simple string message
  if (typeof detail === 'string') return detail

  // Pydantic validation error array
  if (Array.isArray(detail)) {
    return detail
      .map((e: any) => {
        // Remove Pydantic's "Value error, " prefix if present
        const msg: string = (e.msg ?? '').replace(/^Value error,\s*/i, '')
        // Get the field name from loc, skip "body" prefix
        const field = (e.loc ?? [])
          .filter((l: any) => l !== 'body')
          .join(' → ')
        return field ? `${capitalise(field)}: ${msg}` : capitalise(msg)
      })
      .join('\n')
  }

  return fallback
}

function capitalise(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1)
}
