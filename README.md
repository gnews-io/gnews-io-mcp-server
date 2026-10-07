# 📡 GNews API MCP Server

This document describes a **Model Context Protocol (MCP)** server that exposes the GNews API.

This server is already deployed and publicly accessible, so you don't need to install anything.
You just need to connect it to your compatible MCP client (**Claude Code, Gemini CLI, etc.**).

---

## 🔑 GNews API Key

To use this server, you need a valid **GNews API** key.

👉 [Get your API key here](https://gnews.io/)

The API key must be provided in the following way:

- Via an HTTP header `X-Api-Key`

---

## 🔗 MCP Integration

This server is listed in the [official MCP Registry](https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.gnews-io/gnews) as `io.github.gnews-io/gnews`.

### With Claude Code

Add the server to your **Claude Code** configuration with the following command:

```bash
claude mcp add --transport http gnews_api https://mcp.gnews.io/ --header "X-Api-Key: YOUR_API_KEY"
```

## 🛠️ Available Tools

Once the server is connected, the following two tools are available:

- **search**: Search for news articles through a combination of keywords.
- **top_headlines**: Get top headlines by category and country.

---

## 📄 Usage Examples

### Search for articles

This example searches for the **5 latest English articles** on climate change:

```json
{
  "tool": "search",
  "args": {
    "q": "climate change",
    "lang": "en",
    "max": 5
  }
}
```

### Get latest headlines

This example retrieves the **5 top headlines** from the "technology" category in the United States:

```json
{
  "tool": "top_headlines",
  "args": {
    "category": "technology",
    "country": "us",
    "max": 5
  }
}
```

---

## 🔒 Security

- Never share your **API key**. Treat it like a password.
- This server acts as a proxy: it does not store **any API keys**.
  Your key is transmitted directly to **GNews API** with each request.
- Always use an **HTTPS** connection to communicate with the server to ensure your key is encrypted in transit.
- The hosted server records anonymous usage statistics for each tool call: tool name, MCP client name and version, success or error, duration, and the `lang`, `country`, `category`, `max`, `page` and `sortby` parameters.
  Your API key is only recorded as a one-way hash, and your search queries are never recorded.

---

## 📋 Client Prerequisites

- A compatible MCP client (e.g., **Claude Code**).
- The latest version of **Gemini CLI** is recommended for optimal compatibility.
