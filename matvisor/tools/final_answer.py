from smolagents import FinalAnswerTool
from matvisor.log import Logger


class LoggedFinalAnswerTool(FinalAnswerTool):

    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger

    def __call__(self, *args, **kwargs):
        # Some agent executors call tools via __call__ (which then validates and calls run)
        self.logger.log({
            "kind": "tool_call",
            "tool": self.name,          # should be "final_answer"
            "args": args,
            "kwargs": kwargs,
        })
        result = super().__call__(*args, **kwargs)
        # Log the result (it’s typically either the string or an agent sentinel)
        self.logger.log({
            "kind": "tool_result",
            "tool": self.name,
            "result_preview": str(result)[:5000],
        })
        return result
