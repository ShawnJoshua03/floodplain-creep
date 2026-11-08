type ApiFailure = Error & { status: number };

type Params = Record<string, string | number>;

function failure(status: number): ApiFailure {
  return Object.assign(new Error(`The request failed with status ${status}.`), { status });
}

export function isNotFound(error: unknown): boolean {
  return error instanceof Error && "status" in error && error.status === 404;
}

function withQuery(path: string, params?: Params): string {
  if (!params) {
    return path;
  }
  const query = new URLSearchParams(Object.entries(params).map(([key, value]) => [key, String(value)]));
  return `${path}?${query.toString()}`;
}

/** The one place the app calls the network. Response types come from the generated OpenAPI schema. */
export async function getJson<T extends object>(path: string, params?: Params, signal?: AbortSignal): Promise<T> {
  const response = await fetch(withQuery(path, params), { signal });
  if (!response.ok) {
    throw failure(response.status);
  }
  const body: unknown = await response.json();
  if (typeof body !== "object" || body === null) {
    throw failure(response.status);
  }
  return body as T;
}
