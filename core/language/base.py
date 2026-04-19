import json
import re

from models.enums.languages import LanguageEnum
from utils.config import log, settings


class Phrase:
    __slots__ = [lang for lang in LanguageEnum] + ["replaceable"]

    def __init__(self, **translations):
        if "__replaceable" in translations:
            self.replaceable = translations["__replaceable"]
            del translations["__replaceable"]
        else:
            self.replaceable = False

        for lang, translated_text in translations.items():
            setattr(self, lang, translated_text)


class TextsManager:
    @classmethod
    def create_from_json(cls, file_path: str) -> "TextsManager":
        manager = cls()

        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
        for key, sub_level in json_data.items():
            subcategory = manager._create_category(sub_level)
            setattr(manager, key, subcategory)

        return manager

    @classmethod
    def _create_category(cls, data: dict):
        manager = cls()

        if any(lang in data for lang in LanguageEnum):
            return Phrase(**data)
        for key, sub_level in data.items():
            subcategory = manager._create_category(sub_level)
            setattr(manager, key, subcategory)

        return manager


class Translator:
    def __init__(self, selected_language: LanguageEnum):
        self.selected_language = selected_language

    @staticmethod
    def _run_substitutions(text: str, **subs) -> str:
        for sub_key, sub_value in subs.items():
            try:
                text = re.sub("{" + sub_key + "}", sub_value, text)
            except re.error as e:
                log.error(e)
                continue
        return text

    @staticmethod
    def _skip_substitutions(text: str, **subs) -> str:
        if subs:
            log.warning(
                "Substitutions not supported for this phrase! Could it be wrong phrase?"
            )
        return text

    def __call__(self, phrase: Phrase, **subs) -> str:
        sub_func = (
            self._run_substitutions if phrase.replaceable else self._skip_substitutions
        )

        text = getattr(phrase, self.selected_language, None)
        if text:
            return sub_func(text=text, **subs)

        log.warning(f"No text for {self.selected_language} in {phrase}. Trying EN")
        text = getattr(phrase, LanguageEnum.EN, None)
        if text:
            return sub_func(text, **subs)

        log.warning(f"No EN text for {self.selected_language} in {phrase}")
        return settings.MISSING_TEXT_PLACEHOLDER
