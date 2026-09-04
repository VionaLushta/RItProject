// Same-origin requests avoid browser CORS/private-network restrictions in local development.
const DEFAULT_API_BASE_URL = "/api";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, "");

class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

async function requestJson(path, options = {}, baseUrl = API_BASE_URL) {
  let response;

  try {
    response = await fetch(`${baseUrl}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers ?? {}),
      },
      ...options,
    });
  } catch {
    throw new ApiError("CampusMate couldn't complete this request. Please check your connection.", 0, null);
  }

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? await response.json().catch(() => null)
    : await response.text().catch(() => "");

  if (!response.ok) {
    const message =
      payload && typeof payload === "object" && typeof payload.error === "string"
        ? payload.error
        : "CampusMate couldn't complete this request. Please try again.";
    throw new ApiError(message, response.status, payload);
  }

  return payload;
}

async function readSseResponse(response, handlers = {}) {
  if (!response.ok) {
    const contentType = response.headers.get("content-type") ?? "";
    const payload = contentType.includes("application/json")
      ? await response.json().catch(() => null)
      : await response.text().catch(() => "");
    const message =
      payload && typeof payload === "object" && typeof payload.error === "string"
        ? payload.error
        : "CampusMate couldn't complete this request. Please try again.";
    throw new ApiError(message, response.status, payload);
  }

  if (!response.body) {
    throw new ApiError("CampusMate couldn't stream this response. Please try again.", response.status, null);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalAnswer = "";
  let currentEvent = "message";

  function flushEvent(rawEvent) {
    const trimmed = rawEvent.trim();
    if (!trimmed) {
      return;
    }

    const lines = trimmed.split(/\r?\n/);
    let eventName = "message";
    const dataLines = [];

    for (const line of lines) {
      if (line.startsWith("event:")) {
        eventName = line.slice(6).trim();
        continue;
      }

      if (line.startsWith("data:")) {
        dataLines.push(line.slice(5).trimStart());
      }
    }

    const rawData = dataLines.join("\n");
    let payload = null;

    try {
      payload = rawData ? JSON.parse(rawData) : null;
    } catch {
      payload = rawData;
    }

    if (eventName === "delta") {
      const chunk = payload && typeof payload === "object" && typeof payload.chunk === "string" ? payload.chunk : "";
      if (chunk) {
        finalAnswer += chunk;
        handlers.onChunk?.(chunk, finalAnswer);
      }
      return;
    }

    if (eventName === "done") {
      const answer = payload && typeof payload === "object" && typeof payload.answer === "string" ? payload.answer : finalAnswer;
      finalAnswer = answer;
      handlers.onDone?.(answer);
      return;
    }

    if (eventName === "error") {
      const message = payload && typeof payload === "object" && typeof payload.error === "string"
        ? payload.error
        : "CampusMate couldn't complete this request. Please try again.";
      throw new ApiError(message, response.status, payload);
    }
  }

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });

      while (true) {
        const boundary = buffer.indexOf("\n\n");
        if (boundary === -1) {
          break;
        }

        const rawEvent = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        flushEvent(rawEvent);
      }
    }

    buffer += decoder.decode();
    if (buffer.trim()) {
      flushEvent(buffer);
    }
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError("CampusMate couldn't complete this request. Please try again.", response.status, null);
  }

  return finalAnswer;
}

export function apiBaseUrl() {
  return API_BASE_URL;
}

export function askQuestion(question) {
  return requestJson("/ask-ai", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export async function askQuestionStream(question, handlers = {}) {
  const response = await fetch(`${API_BASE_URL}/ask-ai/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(handlers.headers ?? {}),
    },
    body: JSON.stringify({ question }),
    signal: handlers.signal,
  }).catch(() => {
    throw new ApiError("CampusMate couldn't complete this request. Please check your connection.", 0, null);
  });

  return readSseResponse(response, handlers);
}

export function explainTopic(topic, difficulty) {
  return requestJson("/explain-topic", {
    method: "POST",
    body: JSON.stringify({ topic, difficulty }),
  });
}

export function summarizeText(text, style) {
  return requestJson("/summarize", {
    method: "POST",
    body: JSON.stringify({ text, style }),
  });
}

export function generateQuiz(topic, difficulty, questionCount) {
  return requestJson("/generate-quiz", {
    method: "POST",
    body: JSON.stringify({ topic, difficulty, question_count: questionCount }),
  });
}

export function submitQuiz(quiz, answers) {
  return requestJson("/submit-quiz", {
    method: "POST",
    body: JSON.stringify({ quiz, answers }),
  });
}

export function getHistory() {
  return requestWithLocalFallback("/history");
}

export function getStatistics() {
  return requestWithLocalFallback("/statistics");
}

async function requestWithLocalFallback(path) {
  try {
    return await requestJson(path, { method: "GET" });
  } catch (error) {
    const fallbackBase = API_BASE_URL === "/api" ? "http://127.0.0.1:8000/api" : "/api";

    try {
      return await requestJson(path, { method: "GET" }, fallbackBase);
    } catch {
      throw error;
    }
  }
}

export function getHealth() {
  return requestJson("/health", { method: "GET" });
}

export { ApiError };
