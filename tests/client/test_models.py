import pytest

from steamship.data.plugin import PluginAdapterType
from steamship.data.plugin import PluginType
from .helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_model_create():
    steamship = _steamship()
    name = _random_name()

    my_models = steamship.models.listPrivate().data
    orig_count = len(my_models.models)

    # Should require name
    with pytest.raises(Exception):
        index = steamship.models.create(
            description="This is just for test",
            modelType=PluginType.embedder,
            url="http://foo1",
            adapterType=PluginAdapterType.steamshipDocker,
            isPublic=True
        )

    # Should require description
    with pytest.raises(Exception):
        index = steamship.models.create(
            name="Test Model",
            modelType=PluginType.embedder,
            url="http://foo2",
            adapterType=PluginAdapterType.steamshipDocker,
            isPublic=True
        )

    # Should require model type
    with pytest.raises(Exception):
        index = steamship.models.create(
            name="Test Model",
            description="This is just for test",
            url="http://foo3",
            adapterType=PluginAdapterType.steamshipDocker,
            isPublic=True
        )

    # Should require url
    with pytest.raises(Exception):
        index = steamship.models.create(
            name="Test Model",
            description="This is just for test",
            modelType=PluginType.embedder,
            adapterType=PluginAdapterType.steamshipDocker,
            isPublic=True
        )

    # Should require adapter type
    with pytest.raises(Exception):
        index = steamship.models.create(
            name="Test Model",
            description="This is just for test",
            modelType=PluginType.embedder,
            url="http://foo4",
            isPublic=True
        )

    # Should require is public
    with pytest.raises(Exception):
        index = steamship.models.create(
            name="Test Model",
            description="This is just for test",
            modelType=PluginType.embedder,
            url="http://foo5",
            adapterType=PluginAdapterType.steamshipDocker,
        )

    my_models = steamship.models.listPrivate().data
    assert (len(my_models.models) == orig_count)

    model = steamship.models.create(
        name=_random_name(),
        description="This is just for test",
        modelType=PluginType.embedder,
        url="http://foo6",
        adapterType=PluginAdapterType.steamshipDocker,
        isPublic=False
    ).data
    my_models = steamship.models.listPrivate().data
    assert (len(my_models.models) == orig_count + 1)

    # No upsert doesn't work
    modelX = steamship.models.create(
        handle=model.handle,
        name=model.name,
        description="This is just for test",
        modelType=PluginType.embedder,
        url="http://foo7",
        adapterType=PluginAdapterType.steamshipDocker,
        isPublic=False
    )
    assert (modelX.error is not None)
    assert (modelX.data is None)

    # Upsert does work
    model2 = steamship.models.create(
        name=model.name,
        description="This is just for test 2",
        modelType=PluginType.embedder,
        url="http://foo8",
        adapterType=PluginAdapterType.steamshipDocker,
        isPublic=False,
        upsert=True
    ).data

    assert (model2.id == model.id)

    my_models = steamship.models.listPrivate().data
    assert (len(my_models.models) == orig_count + 1)

    assert (model2.id in [model.id for model in my_models.models])
    assert (model2.description in [model.description for model in my_models.models])

    # assert(my_models.models[0].description != model.description)

    steamship.models.delete(model.id)

    my_models = steamship.models.listPrivate().data
    assert (len(my_models.models) == orig_count)


def test_model_public():
    steamship = _steamship()
    name = _random_name()

    resp = steamship.models.listPublic().data
    assert (resp.models is not None)
    models = resp.models

    assert (len(models) > 0)

    # Make sure they can't be deleted.
    res = steamship.models.delete(models[0].id)
    assert (res.error is not None)
    assert (res.data is None)