# 📡 GNews API MCP Server

This document describes a **Model Context Protocol (MCP)** server that exposes the GNews API.

This server is already deployed and publicly accessible, so you don't need to install anything.
You just need to connect it to your compatible MCP client (**Claude Code, Gemini CLI, etc.**).

---

## 🔑 GNews API Key

To use this server, you need a valid **GNews API** key.

👉 [Get your key here](https://gnews.io/)

The API key must be provided in one of the following ways:

- Via an HTTP header `GNEWS_API_KEY` (**recommended method**).
- Via an `api_key` parameter in the tool call (if your MCP client allows it).

---

## 🔗 MCP Integration

### With Claude Code

Add the server to your **Claude Code** configuration with the following command:

```bash
claude mcp add gnews_api -- npx -y mcp-remote@latest https://mcp.gnews.io/ --header "GNEWS_API_KEY: YOUR_API_KEY"
```

⚠️ **Important**: Replace `YOUR_API_KEY` with your personal API key.

---

### With Gemini CLI

#### Option 1: Quick addition

Add the server directly from command line:

```bash
gemini mcp add gnews_api https://mcp.gnews.io/ -t http -H "GNEWS_API_KEY: YOUR_API_KEY"
```

#### Option 2: Add via `settings.json` (recommended)

Edit your `~/.gemini/settings.json` file:

```json
{
  "mcpServers": {
    "gnews_api": {
      "command": "mcp-remote",
      "args": ["https://mcp.gnews.io/"],
      "headers": {
        "GNEWS_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

⚠️ **Important**: Replace `YOUR_API_KEY` with your personal API key.

---

## 🛠️ Available Tools

Once the server is connected, the following two tools are available:

- **gnews_api_search**: Search for news articles through a combination of keywords.
- **gnews_api_top_headlines**: Get top headlines by category and country.

---

## 📄 Usage Examples

### Search for articles

This example searches for the **5 latest English articles** on climate change:

```json
{
  "tool": "gnews_api_search",
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
  "tool": "gnews_api_top_headlines",
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

---

## 📋 Client Prerequisites

- A compatible MCP client (e.g., **Claude Code**).
- The latest version of **Gemini CLI** is recommended for optimal compatibility.
