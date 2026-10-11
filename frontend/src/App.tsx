import { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";
import type { AskResponse, ConceptCard } from "./types";

const MODES = [
  { id: "hybrid_ontology", label: "RAG + ontology" },
  { id: "hybrid", label: "RAG lai" },
  { id: "bm25", label: "BM25" },
  { id: "dense", label: "Vector" },
];

const SAMPLES = [
  "Nam bao nhiêu tuổi thì được kết hôn?",
  "Ly hôn thì chia nhà, chia đất thế nào?",
  "Vợ không chịu ký đơn thì có ly hôn được không?",
  "Muốn lấy vợ nước ngoài thì có cần giấy xác nhận chưa kết hôn không?",
];

type UserMessage = { id: string; role: "user"; text: string };
type AssistantMessage = { id: string; role: "assistant"; result: AskResponse; error?: string };
type Message = UserMessage | AssistantMessage;
type Thread = { id: string; title: string; messages: Message[] };

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

function useNarrow() {
  const [narrow, setNarrow] = useState(() => window.matchMedia("(max-width: 860px)").matches);
  useEffect(() => {
    const media = window.matchMedia("(max-width: 860px)");
    const onChange = () => setNarrow(media.matches);
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);
  return narrow;
}

function useRoute(): [string, (path: string) => void] {
  const [path, setPath] = useState(window.location.hash.replace("#", "") || "/");
  useEffect(() => {
    const onHash = () => setPath(window.location.hash.replace("#", "") || "/");
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);
  return [path, (next) => (window.location.hash = next)];
}

export default function App() {
  const [path, go] = useRoute();
  const [sidebar, setSidebar] = useState(() => window.matchMedia("(min-width: 861px)").matches);
  const narrow = useNarrow();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const active = threads.find((thread) => thread.id === activeId) ?? null;

  function openChat() {
    go("/");
    if (narrow) setSidebar(false);
  }

  function newChat() {
    setActiveId(null);
    openChat();
  }

  function selectThread(id: string) {
    setActiveId(id);
    openChat();
  }

  return (
    <div className={sidebar ? "shell sidebar-open" : "shell"}>
      <aside className="sidebar">
        <div className="sidebar-top">
          <button className="icon-btn" type="button" onClick={() => setSidebar(false)} aria-label="Đóng thanh bên">
            <MenuIcon />
          </button>
          <button className="new-chat" type="button" onClick={newChat}>
            <PlusIcon />
            Đoạn chat mới
          </button>
        </div>
        <nav className="side-nav">
          <button className={path === "/" ? "active" : ""} type="button" onClick={openChat}>
            Hỏi đáp
          </button>
          <button
            className={path === "/ontology" ? "active" : ""}
            type="button"
            onClick={() => {
              go("/ontology");
              if (narrow) setSidebar(false);
            }}
          >
            Ontology
          </button>
        </nav>
        <div className="history">
          <p>Gần đây</p>
          {threads.length === 0 && <span className="empty-history">Chưa có câu hỏi.</span>}
          {threads.map((thread) => (
            <button
              key={thread.id}
              type="button"
              className={thread.id === activeId && path === "/" ? "history-item active" : "history-item"}
              onClick={() => selectThread(thread.id)}
            >
              {thread.title}
            </button>
          ))}
        </div>
        <p className="side-note">
          Tra cứu Luật 52/2014/QH13, Nghị định 126/2014/NĐ-CP và Thông tư 02a/2015/TT-BTP. Không phải tư vấn pháp lý.
        </p>
      </aside>
      {sidebar && narrow && (
        <button className="scrim" type="button" aria-label="Đóng thanh bên" onClick={() => setSidebar(false)} />
      )}
      <div className="main">
        <header className="bar">
          <button className="icon-btn" type="button" onClick={() => setSidebar((open) => !open)} aria-label="Mở thanh bên">
            <MenuIcon />
          </button>
          <strong>{path === "/ontology" ? "Ontology miền" : "Luật Hôn nhân và gia đình"}</strong>
        </header>
        {path === "/ontology" ? (
          <OntologyPage />
        ) : (
          <ChatPage
            thread={active}
            onThread={(thread) => {
              setThreads((current) => {
                const rest = current.filter((item) => item.id !== thread.id);
                return [thread, ...rest];
              });
              setActiveId(thread.id);
            }}
          />
        )}
      </div>
    </div>
  );
}

function ChatPage({ thread, onThread }: { thread: Thread | null; onThread: (thread: Thread) => void }) {
  const [draft, setDraft] = useState("");
  const [mode, setMode] = useState("hybrid_ontology");
  const [loading, setLoading] = useState(false);
  const busy = useRef(false);
  const scroller = useRef<HTMLDivElement>(null);
  const box = useRef<HTMLTextAreaElement>(null);
  const messages = thread?.messages ?? [];

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function ask(text: string) {
    const question = text.trim();
    if (question.length < 3 || busy.current) return;
    busy.current = true;
    const base: Thread = thread ?? { id: uid(), title: question.slice(0, 72), messages: [] };
    const pending: Thread = {
      ...base,
      messages: [...base.messages, { id: uid(), role: "user", text: question }],
    };
    onThread(pending);
    setDraft("");
    setLoading(true);
    if (box.current) box.current.style.height = "auto";
    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, mode }),
      });
      if (!response.ok) throw new Error(`API ${response.status}`);
      const result = (await response.json()) as AskResponse;
      onThread({
        ...pending,
        messages: [...pending.messages, { id: uid(), role: "assistant", result }],
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Không gọi được API";
      onThread({
        ...pending,
        messages: [
          ...pending.messages,
          {
            id: uid(),
            role: "assistant",
            error: message,
            result: {
              question,
              mode,
              concepts: [],
              answer: "Không gọi được máy chủ tra cứu. Hãy kiểm tra API rồi hỏi lại.",
              abstain: true,
              abstain_reason: message,
              citations: [],
              generator: "error",
              disclaimer: "",
            },
          },
        ],
      });
    } finally {
      busy.current = false;
      setLoading(false);
    }
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    void ask(draft);
  }

  function onKey(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void ask(draft);
    }
  }

  return (
    <div className="chat">
      <div className="thread" ref={scroller}>
        {messages.length === 0 ? (
          <div className="welcome">
            <div className="mark">HN</div>
            <h1>Hỏi về hôn nhân và gia đình</h1>
            <p>Câu trả lời bám Điều, Khoản trong kho đã đóng băng. Đây không phải tư vấn pháp lý.</p>
            <div className="suggestions">
              {SAMPLES.map((sample) => (
                <button key={sample} type="button" onClick={() => void ask(sample)}>
                  {sample}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((message) =>
              message.role === "user" ? (
                <div key={message.id} className="msg user">
                  <div className="bubble">{message.text}</div>
                </div>
              ) : (
                <AssistantBubble key={message.id} message={message} />
              ),
            )}
            {loading && (
              <div className="msg assistant">
                <div className="avatar">HN</div>
                <div className="typing" aria-label="Đang tra cứu">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
      <form className="composer" onSubmit={onSubmit}>
        <div className="composer-box">
          <textarea
            ref={box}
            value={draft}
            rows={1}
            placeholder="Hỏi một câu về hôn nhân, tài sản, nuôi con…"
            onChange={(event) => {
              setDraft(event.target.value);
              event.target.style.height = "auto";
              event.target.style.height = `${Math.min(event.target.scrollHeight, 160)}px`;
            }}
            onKeyDown={onKey}
          />
          <div className="composer-bar">
            <label className="mode">
              <span>Chế độ</span>
              <select value={mode} onChange={(event) => setMode(event.target.value)}>
                {MODES.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
            <button className="send" type="submit" disabled={loading || draft.trim().length < 3} aria-label="Gửi">
              <SendIcon />
            </button>
          </div>
        </div>
        <p className="fineprint">
          Không phải tư vấn pháp lý. Thông tư 02a/2015/TT-BTP được ghi nhận hết hiệu lực từ 02/01/2016 và vẫn được trích kèm cảnh báo.
        </p>
      </form>
    </div>
  );
}

function AssistantBubble({ message }: { message: AssistantMessage }) {
  const { result } = message;
  const [openId, setOpenId] = useState<string | null>(result.citations[0]?.provision_id ?? null);
  const modeLabel = useMemo(
    () => MODES.find((item) => item.id === result.mode)?.label ?? result.mode,
    [result.mode],
  );

  return (
    <div className="msg assistant">
      <div className="avatar">HN</div>
      <div className="answer-body">
        <p className={result.abstain ? "lead abstain" : "lead"}>{result.answer}</p>
        {result.concepts.length > 0 && (
          <div className="chips">
            {result.concepts.map((item) => (
              <span key={item.id}>{item.label}</span>
            ))}
          </div>
        )}
        {result.citations.length > 0 && (
          <div className="sources">
            <p>Nguồn trong kho</p>
            {result.citations.map((cite, index) => {
              const open = openId === cite.provision_id;
              return (
                <article key={cite.provision_id} className={open ? "source open" : "source"}>
                  <button type="button" onClick={() => setOpenId(open ? null : cite.provision_id)}>
                    <span className="num">{index + 1}</span>
                    <span>
                      <strong>{cite.label}</strong>
                      <em>
                        Điều {cite.article_no}. {cite.article_title}
                      </em>
                    </span>
                  </button>
                  {open && (
                    <div className="quote">
                      <p>{cite.quote}</p>
                      {!cite.in_force && cite.expiry_note && <p className="warn">{cite.expiry_note}</p>}
                      <a href={cite.source_url} target="_blank" rel="noreferrer">
                        Mở văn bản gốc
                      </a>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}
        {result.abstain && result.citations.length === 0 && (
          <p className="muted">Không gắn trích dẫn vì câu hỏi nằm ngoài kho hoặc không đủ căn cứ.</p>
        )}
        <p className="meta">
          {modeLabel} · {result.generator}
        </p>
      </div>
    </div>
  );
}

function OntologyPage() {
  const [cards, setCards] = useState<ConceptCard[]>([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/concepts")
      .then((response) => {
        if (!response.ok) throw new Error(`API ${response.status}`);
        return response.json();
      })
      .then((data) => setCards(data.concepts))
      .catch((err: Error) => setError(err.message));
  }, []);

  const shown = cards.filter((card) => {
    const blob = `${card.label} ${card.alts.join(" ")}`.toLowerCase();
    return blob.includes(query.toLowerCase().trim());
  });

  return (
    <div className="ontology">
      <div className="ontology-head">
        <h1>Khái niệm và điều luật</h1>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Tìm khái niệm, ví dụ ly hôn, tài sản, nước ngoài"
        />
        <p>{error || `${shown.length} khái niệm`}</p>
      </div>
      <div className="grid">
        {shown.map((card) => (
          <article key={card.id} className="concept">
            <h2>{card.label}</h2>
            {card.alts.length > 0 && <p className="alts">{card.alts.join(" · ")}</p>}
            <ul>
              {card.provisions.map((item) => (
                <li key={item.provision_id}>
                  <strong>{item.label}</strong>
                  <span>{item.article_title}</span>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </div>
  );
}

function MenuIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M4 7h16M4 12h16M4 17h16" />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 19V5M6 11l6-6 6 6" />
    </svg>
  );
}
