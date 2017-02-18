import json
import urllib.request

from babel.core import Locale  # type: ignore

from .mock import FIXTURES_PATH
from wikidata.client import Client
from wikidata.entity import Entity, EntityId, EntityType
from wikidata.multilingual import MultilingualText


def test_entity_equality(fx_client_opener: urllib.request.OpenerDirector,
                         fx_client: Client,
                         fx_loaded_entity: Entity):
    # When entity id and client are the same
    assert fx_loaded_entity is fx_client.get(fx_loaded_entity.id)
    assert fx_loaded_entity == fx_client.get(fx_loaded_entity.id)
    assert hash(fx_loaded_entity) == hash(fx_client.get(fx_loaded_entity.id))
    # When entity id differs
    assert fx_loaded_entity is not fx_client.get(EntityId('Q1299'))
    assert fx_loaded_entity != fx_client.get(EntityId('Q1299'))
    assert hash(fx_loaded_entity) != hash(fx_client.get(EntityId('Q1299')))
    # When client differs
    client = Client(opener=fx_client_opener)
    assert fx_loaded_entity is not client.get(fx_loaded_entity.id)
    assert fx_loaded_entity != client.get(fx_loaded_entity.id)
    assert hash(fx_loaded_entity) != hash(client.get(fx_loaded_entity.id))


def test_entity_label(fx_loaded_entity: Entity,
                      fx_unloaded_entity: Entity):
    assert isinstance(fx_loaded_entity.label, MultilingualText)
    assert fx_loaded_entity.label[Locale.parse('ko')] == '신중현'
    assert fx_loaded_entity.label[Locale.parse('zh_Hant')] == '申重鉉'
    assert isinstance(fx_unloaded_entity.label, MultilingualText)
    assert fx_unloaded_entity.label[Locale.parse('en')] == 'The Beatles'
    assert fx_unloaded_entity.label[Locale.parse('ko')] == '비틀즈'


def test_entity_description(fx_loaded_entity: Entity,
                            fx_unloaded_entity: Entity):
    assert isinstance(fx_loaded_entity.description, MultilingualText)
    assert fx_loaded_entity.description[Locale.parse('ko')] == \
        '대한민국의 록 음악 싱어송라이터 및 기타리스트'
    assert fx_loaded_entity.description[Locale.parse('ja')] == \
        '韓国のロックミュージシャン'
    assert isinstance(fx_unloaded_entity.description, MultilingualText)
    assert fx_unloaded_entity.description[Locale.parse('en')] == \
        'English rock band'
    assert fx_unloaded_entity.description[Locale.parse('ko')] == \
        '영국의 락 밴드'


def test_entity_type(fx_item: Entity,
                     fx_property: Entity,
                     fx_client_opener: urllib.request.OpenerDirector):
    assert fx_item.type == EntityType.item
    assert fx_property.type == EntityType.property
    guess_client = Client(opener=fx_client_opener, entity_type_guess=True)
    item = guess_client.get(EntityId('Q494290'))
    prop = guess_client.get(EntityId('P434'))
    assert item.type == EntityType.item
    assert item.data is None  # entity data shouldn't be loaded
    assert prop.type == EntityType.property
    assert prop.data is None  # entity data shouldn't be loaded
    noguess_client = Client(opener=fx_client_opener, entity_type_guess=False)
    item = noguess_client.get(EntityId('Q494290'))
    prop = noguess_client.get(EntityId('P434'))
    assert item.type == EntityType.item
    assert item.data['type'] == 'item'
    assert prop.type == EntityType.property
    assert prop.data['type'] == 'property'


def test_entity_attributes(fx_unloaded_entity: Entity,
                           fx_loaded_entity: Entity):
    for entity in fx_unloaded_entity, fx_loaded_entity:
        with (FIXTURES_PATH / '{}.json'.format(entity.id)).open('r') as f:
            assert entity.attributes == json.load(f)['entities'][entity.id]


def test_entity_load(fx_unloaded_entity: Entity):
    fx_unloaded_entity.load()
    with (FIXTURES_PATH / 'Q1299.json').open('r') as f:
        assert fx_unloaded_entity.data == json.load(f)['entities']['Q1299']


def test_entity_repr(fx_unloaded_entity: Entity,
                     fx_loaded_entity: Entity):
    assert repr(fx_unloaded_entity) == '<wikidata.entity.Entity Q1299>'
    assert repr(fx_loaded_entity) == \
        "<wikidata.entity.Entity Q494290 'Shin Jung-hyeon'>"