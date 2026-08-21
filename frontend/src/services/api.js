const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, "");

class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

async function requestJson(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
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

export function apiBaseUrl() {
  return API_BASE_URL;
}

export function askQuestion(question) {
  return requestJson("/ask-ai", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
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
  return requestJson("/history", { method: "GET" });
}

export function getStatistics() {
  return requestJson("/statistics", { method: "GET" });
}

export function getHealth() {
  return requestJson("/health", { method: "GET" });
}

export { ApiError };
