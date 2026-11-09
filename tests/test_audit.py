import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import textkit as tk  # noqa: E402
import keywords  # noqa: E402
import score  # noqa: E402
import diff_runs  # noqa: E402

FIX = ROOT / "tests" / "fixtures"
RUBRIC = json.loads((ROOT / "references" / "rubric.json").read_text())
JOBS = json.loads((FIX / "jobs_sample.json").read_text())


def load(name):
    return json.loads((FIX / name).read_text())


class TextkitTest(unittest.TestCase):
    def test_synonyms(self):
        found = tk.find_terms("ReactJS, TS e testes unitários; inglês fluente")
        for t in ("react", "typescript", "testes automatizados", "inglês"):
            self.assertIn(t, found)

    def test_longest_match_first(self):
        found = tk.find_terms("Apps em React Native")
        self.assertIn("react native", found)
        self.assertNotIn("react", found)

    def test_metric(self):
        self.assertTrue(tk.has_metric("reduzi o LCP em 45%"))
        self.assertTrue(tk.has_metric("para 200 mil usuários"))
        self.assertFalse(tk.has_metric("desenvolvi telas novas"))

    def test_rubric_weights_sum_100(self):
        self.assertEqual(sum(s["weight"] for s in RUBRIC["sections"].values()), 100)


class PipelineTest(unittest.TestCase):
    def run_role(self, role_id, profile):
        kw = keywords.build(JOBS, keywords.load_role(role_id, None))
        jobs = keywords.filter_jobs(JOBS["jobs"], kw["role"])
        return score.score(load(profile), kw, RUBRIC, jobs, today="2026-11-06")

    def test_weak_vs_strong(self):
        weak = self.run_role("frontend-senior", "profile_weak.json")
        strong = self.run_role("frontend-senior", "profile_strong.json")
        self.assertLess(weak["overall"], 35)
        self.assertGreater(strong["overall"], 85)
        self.assertTrue(weak["gaps"])
        self.assertTrue(all(0 <= s["score"] <= 100 for s in strong["sections"].values() if s["score"] is not None))

    def test_gaps_sorted_by_priority(self):
        rep = self.run_role("frontend-senior", "profile_weak.json")
        pr = [g["priority"] for g in rep["gaps"]]
        self.assertEqual(pr, sorted(pr, reverse=True))

    def test_unknown_not_punished(self):
        p = load("profile_strong.json")
        p["metrics"]["ssi"]["total"] = None
        kw = keywords.build(JOBS, keywords.load_role("frontend-senior", None))
        rep = score.score(p, kw, RUBRIC, None, today="2026-11-06")
        self.assertTrue(any("SSI" in u for u in rep["unverified"]))
        self.assertGreater(rep["sections"]["atividade"]["score"], 90)

    def test_role_switch_changes_keywords(self):
        fe = self.run_role("frontend-senior", "profile_strong.json")
        fs = self.run_role("fullstack", "profile_strong.json")
        self.assertNotEqual(fe["keywords"]["missing"], fs["keywords"]["missing"])
        self.assertIn("postgresql", fs["keywords"]["missing"])
        self.assertLess(fs["overall"], fe["overall"])

    def test_custom_role(self):
        role = keywords.load_role(None, "Engenheiro de Dados")
        kw = keywords.build(JOBS, role)
        rep = score.score(load("profile_weak.json"), kw, RUBRIC, None, today="2026-11-06")
        self.assertEqual(rep["role"]["id"], "custom")

    def test_diff(self):
        d = diff_runs.diff(self.run_role("frontend-senior", "profile_weak.json"),
                           self.run_role("frontend-senior", "profile_strong.json"))
        self.assertGreater(d["overall_delta"], 40)
        self.assertIn("react", d["keywords_gained"])


if __name__ == "__main__":
    unittest.main()
