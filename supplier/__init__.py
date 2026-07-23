"""Supplier agent package (`adk web` discovery: exposes `root_agent`).

Lazy on purpose (PEP 562): `agent.py` reads model ids from env, so importing the
package eagerly would demand env even for the pure modules (schemas/tools/merge)
— the iter-0 spike's import-time-env trap. ADK's AgentLoader resolves
`root_agent` via hasattr/getattr, which triggers this hook just fine.
"""


def __getattr__(name: str):
    if name == "root_agent":
        from .agent import root_agent

        return root_agent
    raise AttributeError(name)


__all__ = ["root_agent"]
