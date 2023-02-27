export type Config = {
  serverUrl: string | undefined;
  useFeedback: boolean | undefined;
  useLogin: boolean | undefined;
};

export type ChatMessageButton = {
  title: string;
  payload: string;
  button_type: string;
};

export type ChatMessageAttachment = {
  type: string;
  payload: {
    url?: string;
    buttons?: ChatMessageButton[];
  };
};

export type ChatMessage = {
  attachment?: ChatMessageAttachment;
  text?: string;
  intent?: string;
};

export type AgentMessage = {
  recipient: string;
  message: ChatMessage;
  info?: string;
};

export type UserMessage = {
  message: string;
};
