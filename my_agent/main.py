import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from my_agent.env_utils import AGENT_PORT
from my_agent.tools import current_token, _search_count, _detail_count, _profile_count, _behavior_count
from my_agent.agent import create_agent
from my_agent import conversations as conv_store


app = FastAPI(title="Learning Assistant Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    token: str = ""
    conversation_id: str = ""


# ── Conversation CRUD ──────────────────────────────────────────

@app.get("/conversations")
async def list_conversations():
    return conv_store.list_conversations()


@app.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str):
    conv = conv_store.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@app.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    conv_store.delete_conversation(conv_id)
    return {"status": "deleted"}


# ── Health ─────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


# ── Chat Stream ────────────────────────────────────────────────

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    current_token.set(req.token)
    _search_count.set(0)
    _detail_count.set(0)
    _profile_count.set(0)
    _behavior_count.set(0)

    # Load history for multi-turn context
    history = []
    if req.conversation_id:
        history = conv_store.get_history(req.conversation_id)

    # Build messages: history + current user message
    messages = list(history) + [("user", req.message)]

    # Save user message
    conv_id = req.conversation_id or conv_store.create_conversation()
    conv_store.save_message(conv_id, "user", req.message)

    agent = create_agent()

    async def event_generator():
        full_response = ""
        try:
            async for event in agent.astream_events(
                {"messages": messages},
                version="v2",
            ):
                kind = event["event"]

                if kind == "on_tool_start":
                    tool_name = event.get("name", "unknown")
                    yield {
                        "event": "status",
                        "data": json.dumps({"type": "tool_start", "tool": tool_name}, ensure_ascii=False),
                    }

                elif kind == "on_tool_end":
                    tool_name = event.get("name", "unknown")
                    output = event.get("data", {}).get("output", "")
                    if isinstance(output, str) and len(output) > 200:
                        output = output[:200] + "..."
                    yield {
                        "event": "status",
                        "data": json.dumps({"type": "tool_end", "tool": tool_name, "result": str(output)}, ensure_ascii=False),
                    }

                elif kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        full_response += chunk.content
                        yield {
                            "event": "token",
                            "data": json.dumps({"content": chunk.content}, ensure_ascii=False),
                        }

            # Save assistant response
            if full_response:
                conv_store.save_message(conv_id, "assistant", full_response)

            yield {
                "event": "done",
                "data": json.dumps({"status": "complete", "conversation_id": conv_id}, ensure_ascii=False),
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)
