"""No network calls: exercise the offline Jev triage request/response contract."""

import io
import hashlib
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from experiments.v75_joint import jev_triage


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def valid_response():
    return {
        "model": jev_triage.MODEL,
        "answers": {
            "primary_bottleneck": {
                "type": "choice", "choice": "cash_runway", "confidence": 0.8,
                "probabilities": {key: (1.0 if key == "cash_runway" else 0.0)
                                  for key in jev_triage.QUESTIONS["primary_bottleneck"]["criteria"]}},
            "service_stress": {
                "type": "score", "score": 2.0, "confidence": 0.9,
                "probabilities": {"0": 0.0, "1": 0.0, "2": 1.0, "3": 0.0}},
            "liquidity_stress": {
                "type": "score", "score": 3.0, "confidence": 0.9,
                "probabilities": {"0": 0.0, "1": 0.0, "2": 0.0, "3": 1.0}},
        },
        "usage": {"input_tokens": 200, "output_tokens": 30},
    }


class JevTriageTest(unittest.TestCase):
    def setUp(self):
        self.case = jev_triage.load_cases()[0]

    def test_case_studies_have_replay_provenance_and_no_key(self):
        cases = jev_triage.load_cases()
        self.assertEqual(len(cases), 3)
        for case in cases:
            replay = Path(jev_triage.__file__).parent / case["source_replay"]
            self.assertEqual(hashlib.sha256(replay.read_bytes()).hexdigest(),
                             case["replay_file_sha256"])
            self.assertIn("observed_outcome", case["state"])
            self.assertNotIn("api_key", json.dumps(case).lower())

    def test_missing_key_prevents_request(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(jev_triage, "urlopen") as open_mock:
            with self.assertRaisesRegex(jev_triage.JevError, "unavailable"):
                jev_triage.call_jev(self.case)
            open_mock.assert_not_called()

    def test_mocked_endpoint_receives_official_shape_and_safe_output(self):
        secret = "mock-secret-do-not-print"
        response = valid_response()
        response["unexpected_private_field"] = secret

        def fake_open(request, timeout):
            self.assertEqual(request.full_url, jev_triage.API_URL)
            self.assertEqual(request.get_method(), "POST")
            self.assertEqual(request.get_header("Authorization"), f"Bearer {secret}")
            self.assertEqual(timeout, 30)
            payload = json.loads(request.data)
            self.assertEqual(payload["model"], "jev-1.13.0")
            self.assertEqual(set(payload["questions"]), set(jev_triage.QUESTIONS))
            self.assertEqual(payload["state"], self.case["state"])
            self.assertNotIn(secret, request.data.decode())
            return FakeResponse(json.dumps(response).encode())

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": secret}), patch.object(jev_triage, "urlopen", fake_open):
            result = jev_triage.call_jev(self.case)
        self.assertEqual(result["answers"]["primary_bottleneck"]["choice"], "cash_runway")
        self.assertNotIn(secret, json.dumps(result))

    def test_server_echo_of_key_is_redacted(self):
        secret = "mock-secret-do-not-print"

        def fail_open(request, timeout):
            raise HTTPError(request.full_url, 429, "rate limited " + secret,
                            {}, FakeResponse(secret.encode()))

        with patch.dict(os.environ, {"TYPESAFE_API_KEY": secret}), patch.object(jev_triage, "urlopen", fail_open), patch.object(jev_triage.time, "sleep") as sleep_mock:
            with self.assertRaises(jev_triage.JevError) as raised:
                jev_triage.call_jev(self.case)
        self.assertEqual(str(raised.exception), "Jev HTTP status 429")
        self.assertNotIn(secret, str(raised.exception))
        self.assertEqual(sleep_mock.call_count, 2)

    def test_dry_run_needs_no_key_and_makes_no_request(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(jev_triage, "urlopen") as open_mock, patch("sys.stdout", new_callable=io.StringIO) as output:
            result = jev_triage.main(["--case", self.case["id"], "--dry-run"])
            self.assertEqual(result, 0)
            self.assertEqual(json.loads(output.getvalue())["model"], "jev-1.13.0")
            open_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
