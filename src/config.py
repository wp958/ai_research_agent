"""
AI Research Agent - Configuration
"""

import os

# Qwen API (same as your project 1)
QWEN_API_KEY = "key"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-plus"

# Tavily Search API
TAVILY_API_KEY = "key"

# Agent settings
MAX_STEPS = 5          # max tool calls per question
MAX_SEARCH_RESULTS = 3 # number of search results to return

# Web server
WEB_HOST = "127.0.0.1"

WEB_PORT = 5002        # different from project 1
