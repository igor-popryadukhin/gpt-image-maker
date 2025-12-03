from pathlib import Path

from gpt_image_maker.state import LineStatus, State


def test_state_save_and_load(tmp_path: Path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello", encoding="utf-8")
    state_path = tmp_path / "state.json"
    state = State(input_file=input_file, input_hash=State.calculate_hash(input_file))
    state.statuses[1] = LineStatus(status="ok", message=None)
    state.save(state_path)

    loaded = State.load(state_path)
    assert loaded is not None
    assert loaded.input_file == input_file
    assert loaded.input_hash == state.input_hash
    assert 1 in loaded.statuses
    assert loaded.statuses[1].status == "ok"
