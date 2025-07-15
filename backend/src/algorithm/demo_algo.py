from .base_algo import BaseAlgorithm


class DemoAlgorithm(BaseAlgorithm):
    def process(self) -> dict[str, str]:
        super().process()
        return {"hint1": "value1"}
