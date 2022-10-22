from hydra import initialize, compose
from omegaconf import DictConfig

from core.inference_pipeline import InferencePipeline


def get_config() -> DictConfig:
    with initialize(config_path="."):
        # config is relative to a module
        config = compose(config_name="config")
    return config


def init():
    config = get_config()
    inference_object = InferencePipeline(config=config)
    return inference_object


if __name__ == "__main__":
    inference_object = init()
    inference_object.run()
    print(inference_object)
