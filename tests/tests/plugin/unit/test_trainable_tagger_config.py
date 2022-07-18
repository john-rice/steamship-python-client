from unittest.mock import patch

from steamship import File
from steamship.data.block import Block
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.service import PluginRequest
from steamship.plugin.trainable_model import TrainableModel
from tests.assets.plugins.taggers.plugin_trainable_tagger_config import (
    TestConfig,
    TestTrainableTaggerConfigModel,
    TestTrainableTaggerConfigPlugin,
)
from tests.utils.fixtures import get_steamship_client

TEST_REQ = BlockAndTagPluginInput(
    file=File(
        blocks=[
            Block(
                id="ABC",
                text="Once upon a time there was a magical ship. "
                "The ship was powered by STEAM. The ship went to the moon.",
            )
        ]
    )
)
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ, plugin_instance_id="000")
TEST_PLUGIN_REQ_DICT = TEST_PLUGIN_REQ.dict()


def test_trainable_tagger():
    client = get_steamship_client()
    assert client is not None

    def load_remote(**kwargs):
        model = TestTrainableTaggerConfigModel()
        model.receive_config(TestConfig(testValue1=1, testValue2=2))
        return model

    # There isn't ACTUALLY model data to load..
    with patch.object(TrainableModel, "load_remote", load_remote):
        plugin = TestTrainableTaggerConfigPlugin(
            client=client, config={"testValue1": "foo", "testValue2": "bar"}
        )
        assert plugin.client is not None

        # Make sure plugin model gets its config while 'training'.
        plugin.train_endpoint(
            **PluginRequest(
                data=TrainPluginInput(plugin_instance="foo", training_params=None),
                task_id="000",
                plugin_instance_id="000",
            ).dict()
        )

        # Make sure plugin model gets its config while 'running'
        plugin.run(TEST_PLUGIN_REQ)
