from smolagents import Tool
from matvisor.workshop.log import JSONLogger


class LoggedTool(Tool):
    def __init__(self, inner: Tool, logger: JSONLogger):
        # Mirror the inner tool’s required attributes
        self.name = getattr(inner, "name", inner.__class__.__name__)
        self.description = getattr(inner, "description", "No description provided.")
        self.inputs = getattr(inner, "inputs", {})
        self.output_type = getattr(inner, "output_type", "any")

        # Keep references
        self.inner = inner
        self.logger = logger

        # CRITICAL: expose the inner forward (same signature!) before validation
        self.forward = inner.forward

        # Let smolagents validate now that attrs & forward are in place
        super().__init__()

    # Log around execution; delegate to the inner tool’s __call__
    def __call__(self, *args, **kwargs):
        self.logger.log({
            "kind": "tool_call",
            "tool": self.inner.name,
            "args": args,
            "kwargs": kwargs,
        })
        result = self.inner(*args, **kwargs)
        self.logger.log({
            "kind": "tool_result",
            "tool": self.inner.name,
            "result_preview": str(result)[:5000],
        })
        return result
    '''
    def run(self, *args, **kwargs):
        # If the framework calls run(...) directly (common for FinalAnswerTool),
        # we capture that path too.
        self.logger.log({
            "kind": "tool_call",
            "tool": self.inner.name,
            "via": "run",
            "args": args,
            "kwargs": kwargs,
        })
        # Not all Tool subclasses implement run; fall back if needed
        if hasattr(self.inner, "run"):
            result = self.inner.run(*args, **kwargs)
        else:
            result = self.inner.__call__(*args, **kwargs)
        self.logger.log({
            "kind": "tool_result",
            "tool": self.inner.name,
            "via": "run",
            "result_preview": str(result)[:5000],
        })
        return result
    '''