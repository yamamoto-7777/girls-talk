import { useReducer, useEffect, useRef, useCallback } from "react";
import type { VTuberState, VTuberMessage } from "../types/vtuber";

// -------------------- Types --------------------

type Action =
  | { type: "START"; sessionId: string }
  | { type: "START_LOADING" }
  | { type: "FINISH_LOADING"; content: string }
  | { type: "STOP" }
  | { type: "RESET"; sessionId: string }
  | { type: "SET_ERROR"; error: string };

// -------------------- Constants --------------------

const MAX_TURNS = 10;

// -------------------- Initial State --------------------

function createInitialState(): VTuberState {
  return {
    status: "idle",
    messages: [],
    turnCount: 0,
    sessionId: crypto.randomUUID(),
    error: undefined,
  };
}

// -------------------- Helpers --------------------

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

// -------------------- Reducer --------------------

function reducer(state: VTuberState, action: Action): VTuberState {
  switch (action.type) {
    case "START": {
      return {
        ...createInitialState(),
        sessionId: action.sessionId,
        status: "loading",
        error: undefined,
      };
    }

    case "START_LOADING": {
      const newMessage: VTuberMessage = {
        id: generateId(),
        content: "",
        isLoading: true,
      };
      return {
        ...state,
        status: "loading",
        messages: [...state.messages, newMessage],
      };
    }

    case "FINISH_LOADING": {
      const messages = state.messages.map((m, i) =>
        i === state.messages.length - 1
          ? { ...m, content: action.content, isLoading: false }
          : m
      );
      const newTurnCount = state.turnCount + 1;
      const newStatus: VTuberState["status"] =
        newTurnCount >= MAX_TURNS ? "idle" : "speaking";

      return {
        ...state,
        messages,
        turnCount: newTurnCount,
        status: newStatus,
      };
    }

    case "STOP": {
      const messages = state.messages.map((m) =>
        m.isLoading ? { ...m, isLoading: false } : m
      );
      return { ...state, messages, status: "stopped" };
    }

    case "RESET": {
      return {
        ...createInitialState(),
        sessionId: action.sessionId,
      };
    }

    case "SET_ERROR": {
      const messages = state.messages.map((m) =>
        m.isLoading ? { ...m, isLoading: false } : m
      );
      return { ...state, messages, status: "idle", error: action.error };
    }

    default:
      return state;
  }
}

// -------------------- fetch --------------------

const API_URL = import.meta.env.VITE_API_URL ?? "";

async function fetchVTuberTurn(
  topic: string,
  sessionId: string,
  abortSignal: AbortSignal
): Promise<string> {
  const response = await fetch(`${API_URL}/chat/vtuber`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    signal: abortSignal,
    body: JSON.stringify({
      topic,
      sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  const data = await response.json() as { content?: string; error?: string };

  if (data.error) {
    throw new Error(data.error);
  }

  return data.content ?? "";
}

// -------------------- Hook --------------------

export function useVTuberConversation() {
  const [state, dispatch] = useReducer(reducer, undefined, createInitialState);

  const abortControllerRef = useRef<AbortController | null>(null);
  const isFetchingRef = useRef(false);
  // トピックはstateに入れず別管理（API呼び出し用）
  const topicRef = useRef<string>("");

  // loading状態: APIを呼んでコンテンツを取得
  useEffect(() => {
    if (state.status !== "loading") return;

    const lastMessage = state.messages[state.messages.length - 1];
    if (!lastMessage || !lastMessage.isLoading) return;
    if (lastMessage.content !== "") return;
    if (isFetchingRef.current) return;

    isFetchingRef.current = true;
    const controller = new AbortController();
    abortControllerRef.current = controller;
    const signal = controller.signal;

    fetchVTuberTurn(
      topicRef.current,
      state.sessionId,
      signal
    )
      .then((content) => {
        isFetchingRef.current = false;
        dispatch({ type: "FINISH_LOADING", content });
      })
      .catch((err: unknown) => {
        isFetchingRef.current = false;
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }
        dispatch({
          type: "SET_ERROR",
          error: err instanceof Error ? err.message : "Unknown error",
        });
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.messages.length, state.status]);

  // speaking状態: 次ターンへ自動遷移
  useEffect(() => {
    if (state.status !== "speaking") return;

    // 少し間を置いてから次のメッセージをロード（UX向け）
    const timerId = setTimeout(() => {
      dispatch({ type: "START_LOADING" });
    }, 600);

    return () => clearTimeout(timerId);
  }, [state.status, state.turnCount]);

  const start = useCallback((topic: string) => {
    topicRef.current = topic;
    isFetchingRef.current = false;
    abortControllerRef.current?.abort();

    const newSessionId = crypto.randomUUID();
    dispatch({ type: "START", sessionId: newSessionId });
    dispatch({ type: "START_LOADING" });
  }, []);

  const stop = useCallback(() => {
    abortControllerRef.current?.abort();
    isFetchingRef.current = false;
    dispatch({ type: "STOP" });
  }, []);

  const reset = useCallback(() => {
    abortControllerRef.current?.abort();
    isFetchingRef.current = false;
    const newSessionId = crypto.randomUUID();
    dispatch({ type: "RESET", sessionId: newSessionId });
  }, []);

  return { state, start, stop, reset };
}
