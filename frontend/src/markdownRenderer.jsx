import { useEffect, useId, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

let mermaidModulePromise = null;

async function loadMermaid() {
  if (!mermaidModulePromise) {
    mermaidModulePromise = import("mermaid").then((module) => module.default ?? module);
  }

  return mermaidModulePromise;
}

function normalizeMarkdown(content) {
  const lines = content.replace(/\r\n?/g, "\n").split("\n");
  let insideFence = false;

  return lines
    .map((line) => {
      if (/^\s*```/.test(line)) {
        insideFence = !insideFence;
        return line;
      }

      if (insideFence) {
        return line;
      }

      // AI responses sometimes escape Markdown markers or put list items on one line.
      return line
        .replace(/\\([*_`#[\]])/g, "$1")
        .replace(/\s+(?=(?:#{1,6}\s|\d+[.)]\s|[-*+]\s))/g, "\n");
    })
    .join("\n")
    .trim();
}

function MermaidDiagram({ source }) {
  const diagramId = useId().replace(/:/g, "");
  const [rendered, setRendered] = useState({ status: "loading", svg: "", error: "" });

  useEffect(() => {
    let active = true;

    async function renderDiagram() {
      try {
        const mermaid = await loadMermaid();
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "strict",
          theme: "default",
        });

        const result = await mermaid.render(`mermaid-${diagramId}`, source);
        if (!active) {
          return;
        }

        setRendered({ status: "ready", svg: result.svg, error: "" });
      } catch {
        if (active) {
          setRendered({ status: "error", svg: "", error: "Diagram rendering failed." });
        }
      }
    }

    renderDiagram();

    return () => {
      active = false;
    };
  }, [diagramId, source]);

  if (rendered.status === "ready" && rendered.svg) {
    return <div className="mermaid-diagram" dangerouslySetInnerHTML={{ __html: rendered.svg }} />;
  }

  return (
    <div className="mermaid-fallback" role="img" aria-label="Mermaid diagram fallback">
      <p className="mermaid-fallback__title">Mermaid diagram</p>
      {rendered.status === "error" ? <p className="mermaid-fallback__error">{rendered.error}</p> : null}
      <pre className="markdown-pre"><code>{source}</code></pre>
    </div>
  );
}

function MarkdownCode({ className, children, inline, ...props }) {
  const match = /language-(\w+)/.exec(className || "");
  const language = match?.[1]?.toLowerCase();
  const code = String(children).replace(/\n$/, "");

  if (!inline && language === "mermaid") {
    return <MermaidDiagram source={code} />;
  }

  if (inline) {
    return (
      <code className="markdown-inline-code" {...props}>
        {children}
      </code>
    );
  }

  return (
    <pre className="markdown-pre">
      <code className={className} {...props}>
        {children}
      </code>
    </pre>
  );
}

export function MarkdownResponse({ content, className = "" }) {
  const normalizedContent = useMemo(
    () => (typeof content === "string" ? normalizeMarkdown(content) : ""),
    [content],
  );

  if (!normalizedContent.trim()) {
    return null;
  }

  return (
    <div className={`markdown-response ${className}`.trim()}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code: MarkdownCode,
          h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
          h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
          h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
          h4: ({ children }) => <h4 className="markdown-h4">{children}</h4>,
          p: ({ children }) => <p className="markdown-p">{children}</p>,
          ul: ({ children }) => <ul className="markdown-ul">{children}</ul>,
          ol: ({ children }) => <ol className="markdown-ol">{children}</ol>,
          li: ({ children }) => <li className="markdown-li">{children}</li>,
          blockquote: ({ children }) => <blockquote className="markdown-blockquote">{children}</blockquote>,
          table: ({ children }) => <div className="markdown-table-wrap"><table className="markdown-table">{children}</table></div>,
          thead: ({ children }) => <thead className="markdown-thead">{children}</thead>,
          tbody: ({ children }) => <tbody className="markdown-tbody">{children}</tbody>,
          tr: ({ children }) => <tr className="markdown-tr">{children}</tr>,
          th: ({ children }) => <th className="markdown-th">{children}</th>,
          td: ({ children }) => <td className="markdown-td">{children}</td>,
          a: ({ children, href }) => (
            <a className="markdown-link" href={href} target="_blank" rel="noreferrer">
              {children}
            </a>
          ),
        }}
      >
        {normalizedContent}
      </ReactMarkdown>
    </div>
  );
}
