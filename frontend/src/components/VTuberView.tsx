import { useState, useEffect, useRef } from "react";
import { useVTuberConversation } from "../hooks/useVTuberConversation";
import type { VTuberMessage } from "../types/vtuber";
import styles from "./VTuberView.module.css";

// -------------------- VTuberキャラクター定義 --------------------

const VTUBER = {
  name: "アイ",
  color: "#4A90D9",
} as const;

// -------------------- MessageBubble --------------------

function VTuberMessageBubble({ message }: { message: VTuberMessage }) {
  return (
    <div className={styles.messageWrapper}>
      <div
        className={styles.avatar}
        style={{ background: VTUBER.color }}
        aria-hidden="true"
      >
        {VTUBER.name[0]}
      </div>
      <div className={styles.messageBody}>
        <div className={styles.speakerName} style={{ color: VTUBER.color }}>
          {VTUBER.name}
        </div>
        <div
          className={styles.bubble}
          style={{ borderColor: VTUBER.color }}
        >
          <span className={styles.content}>{message.content}</span>
          {message.isLoading && (
            <span className={styles.cursor} aria-hidden="true" />
          )}
        </div>
      </div>
    </div>
  );
}

// -------------------- Main Component --------------------

export function VTuberView() {
  const { state, start, stop, reset } = useVTuberConversation();
  const [topicValue, setTopicValue] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const isActive = state.status === "loading" || state.status === "speaking";

  // 新しいメッセージが追加されたら自動スクロール
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [state.messages.length]);

  // ローディング中のコンテンツ更新時もスクロール
  const lastMessage = state.messages[state.messages.length - 1];
  useEffect(() => {
    if (lastMessage?.isLoading) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [lastMessage?.content, lastMessage?.isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = topicValue.trim();
    if (!trimmed) return;
    start(trimmed);
  };

  const handleReset = () => {
    reset();
    setTopicValue("");
  };

  return (
    <div className={styles.container}>
      {/* トピック入力 */}
      <form className={styles.inputArea} onSubmit={handleSubmit}>
        <input
          className={styles.topicInput}
          type="text"
          value={topicValue}
          onChange={(e) => setTopicValue(e.target.value)}
          placeholder="今日の配信トピックを入力してください（例: 最近ハマっているアニメ）"
          disabled={isActive}
          aria-label="VTuber会話のトピック"
          maxLength={200}
        />
        <button
          className={styles.startButton}
          type="submit"
          disabled={isActive || topicValue.trim() === ""}
          aria-label="VTuber会話を開始する"
        >
          開始
        </button>
        {isActive && (
          <button
            className={styles.stopButton}
            type="button"
            onClick={stop}
            aria-label="VTuber会話を停止する"
          >
            停止
          </button>
        )}
        {!isActive && state.messages.length > 0 && (
          <button
            className={styles.resetButton}
            type="button"
            onClick={handleReset}
            aria-label="リセットして新しい会話を始める"
          >
            リセット
          </button>
        )}
      </form>

      {/* エラー表示 */}
      {state.error && (
        <div className={styles.errorBanner} role="alert" aria-live="polite">
          <span>{state.error}</span>
        </div>
      )}

      {/* 会話表示エリア */}
      <div
        className={styles.chatArea}
        role="log"
        aria-live="polite"
        aria-label="VTuber会話ログ"
      >
        {state.messages.length === 0 ? (
          <div className={styles.emptyState}>
            <p className={styles.emptyText}>
              トピックを入力して「開始」を押すと、アイの配信がスタートします
            </p>
          </div>
        ) : (
          <div className={styles.messages}>
            {state.messages.map((message) => (
              <VTuberMessageBubble key={message.id} message={message} />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* ステータスパネル */}
      <div className={styles.statusPanel}>
        <div className={styles.turnInfo} aria-label={`ターン数: ${state.turnCount} / 10`}>
          <span className={styles.turnCount}>
            {state.turnCount} <span className={styles.separator}>/</span> 10 ターン
          </span>
          {isActive && (
            <span className={styles.statusBadge} aria-label="配信中">
              <span className={styles.dot} aria-hidden="true" />
              配信中
            </span>
          )}
          {state.status === "stopped" && (
            <span className={styles.stoppedBadge}>停止済み</span>
          )}
          {state.status === "idle" && state.turnCount > 0 && (
            <span className={styles.doneBadge}>完了</span>
          )}
        </div>
      </div>
    </div>
  );
}
