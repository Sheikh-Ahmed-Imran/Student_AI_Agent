"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, Send } from "lucide-react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { v4 as uuidv4 } from "uuid";

interface Message {
  id: string;
  content: string;
  sender: "user" | "agent";
  timestamp: Date;
}

interface Conversation {
  id: string;
}

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch conversation IDs from backend
  useEffect(() => {
    const fetchConversations = async () => {
      setIsLoading(true);
      try {
        const res = await fetch("http://127.0.0.1:8000/conversations");
        const data = await res.json();
        const convs = data.conversation_ids.map((id: string) => ({ id }));
        setConversations(convs);

        if (convs.length > 0) {
          handleConversationSelect(convs[0].id);
        }
      } catch (err) {
        console.error("Failed to fetch conversations:", err);
      }
      setIsLoading(false);
    };
    fetchConversations();
  }, []);

  // Fetch messages for selected conversation
  const handleConversationSelect = async (conversationId: string) => {
    setSelectedConversation(conversationId);
    setLoadingMessages(true);

    // If this conversation is new (not yet in backend), show placeholder
    if (!conversations.find(c => c.id === conversationId)) {
      setMessages([]);
      setLoadingMessages(false);
      return;
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/conversations/${conversationId}`);
      const data = await res.json();
      const mappedMessages: Message[] = data.messages.map((msg: any, idx: number) => ({
        id: idx.toString(),
        content: msg.content,
        sender: msg.role === "user" ? "user" : "agent",
        timestamp: new Date(msg.created_at),
      }));
      setMessages(mappedMessages);
    } catch (err) {
      console.error("Failed to fetch messages:", err);
      setMessages([]);
    }
    setLoadingMessages(false);
  };

  // Send user message and get AI reply
  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: newMessage,
      sender: "user",
      timestamp: new Date(),
    };

    // Add user's message locally
    setMessages(prev => [...prev, userMessage]);
    setNewMessage("");

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: selectedConversation,
        }),
      });

      const data = await res.json();

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.reply,
        sender: "agent",
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, agentMessage]);

      // If it was a new conversation, save conversation_id from backend
      if (!selectedConversation) {
        setSelectedConversation(data.conversation_id);
        setConversations(prev => [{ id: data.conversation_id }, ...prev]);
      }

    } catch (err) {
      console.error("Failed to send message:", err);
      const errorMsg: Message = {
        id: (Date.now() + 2).toString(),
        content: "Failed to get response from AI.",
        sender: "agent",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    }
  };

  // Create new conversation
  const handleNewConversation = () => {
    const newId = uuidv4();
    const newConv: Conversation = { id: newId };
    setConversations(prev => [newConv, ...prev]);
    setSelectedConversation(newId);
    setMessages([]);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-6">
      {/* Conversation Sidebar */}
      <Card className="w-80 flex flex-col">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="font-semibold text-foreground">Conversations</h2>
          <Button size="sm" variant="outline" onClick={handleNewConversation}>
            <Plus className="h-4 w-4 mr-1" />
            New
          </Button>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-2">
            {isLoading && <p className="text-muted-foreground text-sm">Loading...</p>}

            {!isLoading && conversations.length === 0 && (
              <p className="text-muted-foreground text-sm text-center mt-4">
                No conversations found.
              </p>
            )}

            {!isLoading &&
              conversations.map(conv => (
                <button
                  key={conv.id}
                  onClick={() => handleConversationSelect(conv.id)}
                  className={cn(
                    "w-full text-left p-3 rounded-lg mb-2 transition-colors",
                    selectedConversation === conv.id
                      ? "bg-primary/10 border border-primary/20"
                      : "hover:bg-muted/50"
                  )}
                >
                  <h3 className="font-medium text-sm text-foreground truncate">{conv.id}</h3>
                </button>
              ))}
          </div>
        </ScrollArea>
      </Card>

      {/* Chat Area */}
      <Card className="flex-1 flex flex-col">
        <div className="p-4 border-b border-border">
          <h2 className="font-semibold text-foreground">AI Campus Agent</h2>
        </div>

        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {loadingMessages && <p className="text-muted-foreground text-sm">Loading messages...</p>}

            {!loadingMessages && messages.length === 0 && (
              <p className="text-muted-foreground text-sm text-center mt-4">
                Start typing to begin the conversation...
              </p>
            )}

            {!loadingMessages &&
              messages.map(msg => (
                <div
                  key={msg.id}
                  className={cn(
                    "flex w-max max-w-[75%] rounded-lg px-3 py-2 whitespace-pre-wrap break-words",
                    msg.sender === "user"
                      ? "ml-auto bg-chat-user-bg text-white"
                      : "bg-chat-agent-bg text-foreground"
                  )}
                >
                  <p className="text-sm">{msg.content}</p>
                </div>
              ))}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        <div className="p-4 border-t border-border">
          <div className="flex gap-2">
            <Input
              placeholder="Type your message..."
              value={newMessage}
              onChange={e => setNewMessage(e.target.value)}
              onKeyPress={e => e.key === "Enter" && handleSendMessage()}
              className="flex-1"
            />
            <Button onClick={handleSendMessage} disabled={!newMessage.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
