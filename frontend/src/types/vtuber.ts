export type VTuberMessage = {
  id: string;
  content: string;
  isLoading: boolean;
};

export type VTuberStatus = "idle" | "loading" | "speaking" | "stopped";

export type VTuberState = {
  status: VTuberStatus;
  messages: VTuberMessage[];
  turnCount: number;
  sessionId: string;
  error?: string;
};
