import os

from langchain_openai import ChatOpenAI

from my_agent.env_utils import ZHIPU_API_KEY, ZHIPU_BASE_URL, DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, DEEPSEEK_API_KEY, \
    DEEPSEEK_BASE_URL

# llm = ChatOpenAI(
#     model="deepseek-v4-flash",
#     api_key=DEEPSEEK_API_KEY,
#     base_url=DEEPSEEK_BASE_URL,
# )
#
# llm = ChatOpenAI(
#     model="qwen3.6-flash",
#     api_key=DASHSCOPE_API_KEY,
#     base_url=DASHSCOPE_BASE_URL,
# )

llm = ChatOpenAI(
    model="glm-5.1",
    api_key=ZHIPU_API_KEY,
    base_url=ZHIPU_BASE_URL,
)
