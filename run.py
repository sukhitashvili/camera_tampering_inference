import hydra

from omegaconf import DictConfig


@hydra.main(config_name="config.yaml")
def test_inference(config: DictConfig):
    pass
