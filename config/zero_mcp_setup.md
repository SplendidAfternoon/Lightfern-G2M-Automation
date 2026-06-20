# Zero MCP Setup (Cursor)

Zero MCP uses **OAuth** — not your API key. The REST API key in `.env` is separate (for `push_pipeline.py`).

## Correct config (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "zero": {
      "url": "https://api.zero.inc/mcp"
    }
  }
}
```

Do **not** add `Authorization: Bearer` headers — Zero MCP authenticates via browser OAuth.

## Fix steps

1. **Save** the config above (already updated in your global `mcp.json`).
2. **Fully quit and restart Cursor** (MCP loads at startup).
3. Open **Cursor Settings → Tools & MCP**.
4. Find **zero** — if status is red, click **Connect** / **Login** / **Needs authentication**.
5. Complete **Zero OAuth** in the browser:
   - Sign in to Zero
   - Select your workspace (Lightfern / "Your mom")
   - Authorize the connection
6. Return to Cursor — status should turn **green**.
7. Test in **Agent** chat: "List my Zero CRM contacts"

## Common errors

| Error | Fix |
|---|---|
| Red / errored server | OAuth not completed — click Connect in Settings |
| Missing Authorization | Don't use API key in MCP; use OAuth flow |
| Invalid transport | Remove `"transport": "streamableHttp"` from mcp.json |
| Tools not showing | Restart Cursor; use Agent mode (not Ask) |
| Wrong workspace | Disconnect MCP and re-auth, pick correct workspace |

## You don't need MCP for the hackathon demo

Contacts are already pushed via API:

```powershell
python push_pipeline.py
```

MCP is optional for live "show contacts in Zero" during the demo. If MCP keeps failing, screenshot Zero in the browser instead.

## API vs MCP

| Method | Auth | Use for |
|---|---|---|
| `push_pipeline.py` | Bearer API key in `.env` | Bulk import scored contacts |
| Zero MCP | OAuth in browser | Agent queries/updates CRM in chat |
