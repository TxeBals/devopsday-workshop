from forja.fake_llm import FakeLLM, call, say
from forja.harness import Forja
from forja.session import Checkpoints, Transcript


def test_transcript_roundtrip(tmp_path):
    t = Transcript(tmp_path)
    t.append({"role": "user", "content": "hola"}, {"role": "assistant", "content": "qué tal"})
    t.append({"role": "user", "content": "segunda"})
    assert [m["content"] for m in Transcript.load(tmp_path, t.session_id)] == ["hola", "qué tal", "segunda"]
    t.mark_compaction([{"role": "user", "content": "[Resumen] x"}])
    t.append({"role": "assistant", "content": "sigo"})
    assert [m["content"] for m in Transcript.load(tmp_path, t.session_id)] == ["[Resumen] x", "sigo"]
    assert Transcript.list_sessions(tmp_path)[0] == (t.session_id, "hola")


def test_checkpoints(tmp_path):
    a, b = tmp_path / "a.txt", tmp_path / "nuevo.txt"
    a.write_text("original")
    cp = Checkpoints()
    cp.begin_turn()
    cp.before_write(a)
    a.write_text("v1")
    cp.before_write(a)  # segunda escritura en el mismo turno: se conserva el ORIGINAL
    a.write_text("v2")
    cp.before_write(b)
    b.write_text("creado")
    cp.begin_turn()  # turno sin cambios: undo lo salta
    assert sorted(p.name for p in cp.undo()) == ["a.txt", "nuevo.txt"]
    assert a.read_text() == "original" and not b.exists()
    assert cp.undo() == []


def test_harness_resume_and_undo(project, home):
    llm = FakeLLM([call("read_file", path="facturas/fechas.py"),
                   call("edit_file", path="facturas/fechas.py", old_string="dias: int = 30", new_string="dias: int = 60"),
                   say("cambiado")])
    app = Forja(llm, project, mode="accept_edits", home=home)
    app.turn("cambia los días")
    assert "dias: int = 60" in (project / "facturas/fechas.py").read_text()
    assert [p.name for p in app.undo()] == ["fechas.py"] and "dias: int = 30" in (project / "facturas/fechas.py").read_text()
    sid = app.transcript.session_id
    app2 = Forja(FakeLLM([say("me acuerdo")]), project, home=home)
    app2.resume(sid)
    assert app2.history == app.history
    app2.turn("¿qué hiciste?")
    assert len(Transcript.load(project / ".forja" / "sessions", sid)) == len(app.history) + 2
