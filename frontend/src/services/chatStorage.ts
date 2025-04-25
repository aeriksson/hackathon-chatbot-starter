import { ChatSession } from "../rest/modules/chat";

// Type for storing basic session info
export interface StoredChatSession {
  id: string;
  title: string; // Generated from first message or date
  lastMessage?: string;
  lastUpdated: string;
}

const CHATS_STORAGE_KEY = 'customer_support_chats';
const ACTIVE_CHAT_KEY = 'active_chat_id';

// Get all chat sessions from session storage
export const getStoredChats = (): StoredChatSession[] => {
  const chatsJson = sessionStorage.getItem(CHATS_STORAGE_KEY);
  if (!chatsJson) return [];

  try {
    return JSON.parse(chatsJson);
  } catch (e) {
    // Error parsing stored chats
    return [];
  }
};

// Save a chat session to storage
export const storeChat = (chat: StoredChatSession): void => {
  const chats = getStoredChats();

  // Check if chat already exists
  const existingIndex = chats.findIndex(c => c.id === chat.id);
  if (existingIndex >= 0) {
    // Update existing chat
    chats[existingIndex] = chat;
  } else {
    // Add new chat
    chats.push(chat);
  }

  // Sort by last updated date (newest first)
  chats.sort((a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime());

  // Save to session storage
  sessionStorage.setItem(CHATS_STORAGE_KEY, JSON.stringify(chats));
};

// Remove a chat from storage
export const removeStoredChat = (chatId: string): void => {
  const chats = getStoredChats().filter(chat => chat.id !== chatId);
  sessionStorage.setItem(CHATS_STORAGE_KEY, JSON.stringify(chats));

  // If removing the active chat, clear the active chat
  if (getActiveChat() === chatId) {
    setActiveChat(null);
  }
};

// Get title for a new chat (based on time if no message)
export const getChatTitle = (firstMessage?: string): string => {
  if (firstMessage && firstMessage.trim()) {
    // Use the first few words of the message
    const words = firstMessage.trim().split(/\s+/);
    const titleWords = words.slice(0, 5);
    let title = titleWords.join(' ');

    // Add ellipsis if truncated
    if (words.length > 5) {
      title += '...';
    }

    return title;
  }

  // Default to date/time if no message
  return new Date().toLocaleString();
};

// Update a chat title
export const updateChatTitle = (chatId: string, title: string): void => {
  const chats = getStoredChats();
  const chat = chats.find(c => c.id === chatId);

  if (chat) {
    chat.title = title;
    sessionStorage.setItem(CHATS_STORAGE_KEY, JSON.stringify(chats));
  }
};

// Update the last message for a chat
export const updateChatLastMessage = (chatId: string, message: string): void => {
  const chats = getStoredChats();
  const chat = chats.find(c => c.id === chatId);

  if (chat) {
    chat.lastMessage = message;
    chat.lastUpdated = new Date().toISOString();
    storeChat(chat);
  }
};

// Store a new chat from the API response
export const addChatFromApi = (chat: ChatSession, firstMessage?: string): void => {
  const storedChat: StoredChatSession = {
    id: chat.id,
    title: getChatTitle(firstMessage),
    lastUpdated: chat.updated_at || new Date().toISOString()
  };

  storeChat(storedChat);
};

// Set the active chat in session storage
export const setActiveChat = (chatId: string | null): void => {
  if (chatId) {
    sessionStorage.setItem(ACTIVE_CHAT_KEY, chatId);
  } else {
    sessionStorage.removeItem(ACTIVE_CHAT_KEY);
  }
};

// Get the active chat from session storage
export const getActiveChat = (): string | null => {
  return sessionStorage.getItem(ACTIVE_CHAT_KEY);
};

// Removed setPendingMessage and getPendingMessage functionality
