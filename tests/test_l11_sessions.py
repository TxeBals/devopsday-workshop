from forja.fake_llm import FakeLLM, call, say
from forja.harness import Forja
from forja.session import Checkpoints, Transcript


def test_transcript_roundtrip(tmp_path):
    t = Transcript(tmp_path)
    t.append({"role": "user", "content": "hello"}, {"role": "assistant", "content": "how are you"})
    t.append({"role": "user", "content": "second"})
    assert [m["content"] for m in Transcript.load(tmp_path, t.session_id)] == ["hello", "how are you", "second"]
    t.mark_compaction([{"role": "user", "content": "[Summary] x"}])
    t.append({"role": "assistant", "content": "continuing"})
    assert [m["content"] for m in Transcript.load(tmp_path, t.session_id)] == ["[Summary] x", "continuing"]
    assert Transcript.list_sessions(tmp_path)[0] == (t.session_id, "hello")


def test_checkpoints(tmp_path):
    a, b = tmp_path / "a.txt", tmp_path / "new.txt"
    a.write_text("original")
    cp = Checkpoints()
    cp.begin_turn()
    cp.before_write(a)
    a.write_text("v1")
    cp.before_write(a)  # second write in the same turn: the ORIGINAL is kept
    a.write_text("v2")
    cp.before_write(b)
    b.write_text("created")
    cp.begin_turn()  # turn without changes: undo skips it
    assert sorted(p.name for p in cp.undo()) == ["a.txt", "new.txt"]
    assert a.read_text() == "original" and not b.exists()
    assert cp.undo() == []


def test_harness_resume_and_undo(project, home):
    llm = FakeLLM([call("read_file", path="invoices/dates.py"),
                   call("edit_file", path="invoices/dates.py", old_string="days: int = 30", new_string="days: int = 60"),
                   say("changed")])
    app = Forja(llm, project, mode="accept_edits", home=home)
    app.turn("change the days")
    assert "days: int = 60" in (project / "invoices/dates.py").read_text()
    assert [p.name for p in app.undo()] == ["dates.py"] and "days: int = 30" in (project / "invoices/dates.py").read_text()
    sid = app.transcript.session_id
    app2 = Forja(FakeLLM([say("I remember")]), project, home=home)
    app2.resume(sid)
    assert app2.history == app.history
    app2.turn("what did you do?")
    assert len(Transcript.load(project / ".forja" / "sessions", sid)) == len(app.history) + 2
