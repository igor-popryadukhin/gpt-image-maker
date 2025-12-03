from gpt_image_maker.prompt_builder import PromptBuilder


def test_build_prompt_success():
    template = "{brand} {model}"
    builder = PromptBuilder(template)
    result = builder.build({"brand": "Nissan", "model": "Leaf"})
    assert result == "Nissan Leaf"


def test_build_prompt_missing_placeholder():
    builder = PromptBuilder("{brand} {missing}")
    try:
        builder.build({"brand": "Test"})
    except KeyError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("Expected KeyError for missing placeholder")
