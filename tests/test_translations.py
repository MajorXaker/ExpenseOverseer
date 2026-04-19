import json
import logging

import pytest

from core.language.base import Phrase, TextsManager, Translator  # adjust import
from models.enums.languages import LanguageEnum
from utils.config import settings


@pytest.fixture
def sample_json_data():
    return {
        "analytics": {
            "help": {
                "en": "Analytical data could be shown as chart or exported into csv",
                "ru": "Аналитические данные могут быть отображены в виде "
                "диаграммы или экспортированы в CSV-файл",
                "be": "Аналітычныя дадзеныя могуць быць паказаны як "
                "дыяграма або экспартаваны ў CSV-файл",
            }
        },
        "transactions": {
            "new": {
                "fail": {
                    "en": "Failed to record: unrecognizable amount ",
                    "ru": "Не удалось сохранить: нераспознанная сумма",
                    "be": "Не атрымалася захаваць: нераспазнаная сума",
                }
            }
        },
    }


@pytest.fixture
def json_file(tmp_path, sample_json_data):
    file_path = tmp_path / "texts.json"
    file_path.write_text(json.dumps(sample_json_data), encoding="utf-8")
    return file_path


def test_phrase_default_replaceable_false():
    phrase = Phrase(en="Hello")
    assert phrase.replaceable is False


def test_phrase_replaceable_flag():
    phrase = Phrase(en="Hello {name}", __replaceable=True)
    assert phrase.replaceable is True


def test_phrase_sets_language_attributes():
    phrase = Phrase(en="Hello", ru="Привет", be="Прывітанне")

    assert phrase.en == "Hello"
    assert phrase.ru == "Привет"
    assert phrase.be == "Прывітанне"


def test_phrase_disallows_unknown_attributes():
    phrase = Phrase(en="Hello")

    with pytest.raises(AttributeError):
        phrase.pl = "Cześć"


def test_phrase_slots_match_language_enum():
    expected_slots = [lang for lang in LanguageEnum] + ["replaceable"]
    assert Phrase.__slots__ == expected_slots


def test_create_from_json_builds_nested_structure(json_file):
    manager = TextsManager.create_from_json(str(json_file))

    assert isinstance(manager.analytics.help, Phrase)
    assert isinstance(manager.transactions.new.fail, Phrase)


def test_create_from_json_loads_transactions_fail_translations(json_file):
    manager = TextsManager.create_from_json(str(json_file))

    assert (
        manager.transactions.new.fail.en == "Failed to record: unrecognizable amount "
    )
    assert (
        manager.transactions.new.fail.ru == "Не удалось сохранить: нераспознанная сумма"
    )
    assert (
        manager.transactions.new.fail.be == "Не атрымалася захаваць: нераспазнаная сума"
    )


def test_create_category_returns_phrase_for_language_dict():
    data = {"en": "Hello", "ru": "Привет", "be": "Прывітанне"}

    result = TextsManager._create_category(data)

    assert isinstance(result, Phrase)
    assert result.en == "Hello"
    assert result.ru == "Привет"
    assert result.be == "Прывітанне"


def test_translator_returns_selected_language_text_be():
    phrase = Phrase(en="Hello", ru="Привет", be="Прывітанне")
    translator = Translator(LanguageEnum.BE)

    assert translator(phrase) == "Прывітанне"


def test_translator_works_with_loaded_json_phrase(json_file):
    manager = TextsManager.create_from_json(str(json_file))
    translator = Translator(LanguageEnum.RU)

    result = translator(manager.analytics.help)

    assert result == (
        "Аналитические данные могут быть отображены в виде диаграммы "
        "или экспортированы в CSV-файл"
    )


def test_translator_falls_back_to_english_when_selected_language_missing(caplog):
    phrase = Phrase(en="Hello")
    translator = Translator(LanguageEnum.RU)

    with caplog.at_level(logging.WARNING):
        result = translator(phrase)

    assert result == "Hello"
    assert any("Trying EN" in record.message for record in caplog.records)


def test_translator_returns_placeholder_when_selected_and_english_missing(
    caplog, monkeypatch
):
    phrase = Phrase(ru="Привет")
    translator = Translator(LanguageEnum.BE)

    monkeypatch.setattr(
        settings, "MISSING_TEXT_PLACEHOLDER", "<missing>", raising=False
    )

    with caplog.at_level(logging.WARNING):
        result = translator(phrase)

    assert result == "<missing>"
    assert any("Trying EN" in record.message for record in caplog.records)
    assert any("No EN text" in record.message for record in caplog.records)


def test_run_substitutions_replaces_placeholders():
    result = Translator._run_substitutions(
        "Hello {name}, amount: {amount}",
        name="Alex",
        amount="42",
    )

    assert result == "Hello Alex, amount: 42"


def test_run_substitutions_keeps_text_when_no_subs():
    result = Translator._run_substitutions("Hello world")
    assert result == "Hello world"


def test_skip_substitutions_returns_same_text(caplog):
    with caplog.at_level(logging.WARNING):
        result = Translator._skip_substitutions("Hello", name="Alex")

    assert result == "Hello"
    assert any(
        "Substitutions not supported for this phrase" in record.message
        for record in caplog.records
    )


def test_translator_applies_substitutions_for_replaceable_phrase():
    phrase = Phrase(en="Hello {name}", __replaceable=True)
    translator = Translator(LanguageEnum.EN)

    result = translator(phrase, name="Alex")

    assert result == "Hello Alex"


def test_translator_skips_substitutions_for_non_replaceable_phrase(caplog):
    phrase = Phrase(en="Hello {name}", __replaceable=False)
    translator = Translator(LanguageEnum.EN)

    with caplog.at_level(logging.WARNING):
        result = translator(phrase, name="Alex")

    assert result == "Hello {name}"
    assert any(
        "Substitutions not supported for this phrase" in record.message
        for record in caplog.records
    )


def test_run_substitutions_logs_regex_error_and_continues(caplog):
    with caplog.at_level(logging.ERROR):
        result = Translator._run_substitutions(
            "Hello {name}",
            **{"bad[": "X"},
        )

    assert result == "Hello {name}"
    assert any(record.levelno == logging.ERROR for record in caplog.records)
