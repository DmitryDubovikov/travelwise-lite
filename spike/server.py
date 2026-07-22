"""Spike: expose the hello agent as an A2A service via the framework.
`to_a2a()` generates and serves the agent card at the well-known path."""

import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from spike.remote_hello.agent import _env, root_agent

port = int(_env("SUPPLIER_PORT"))  # set by Makefile / .env — no default in code
app = to_a2a(root_agent, port=port)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=port)
