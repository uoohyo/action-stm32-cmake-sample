import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / '.github/scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result
results = module('test_results')
outputs = module('verify_output')

class ResultsTests(unittest.TestCase):
    def setUp(self):
        self.run = {'headSha': 'abc', 'databaseId': 12, 'attempt': 2,
                    'conclusion': 'success', 'updatedAt': '2026-10-24T00:00:00Z'}
        self.records = [dict(schema_version=2, version='1.2.3', configuration=c,
                             head_sha='abc', run_id='12', run_attempt='2',
                             branch='main', status='success') for c in results.CONFIGS]
    def summary(self):
        return results.summarize('1.2.3', self.run, self.records, 'owner/repo')
    def test_both_configs_pass(self):
        self.assertEqual(self.summary()['status'], 'success')
    def test_release_failure_is_failure(self):
        self.records[1]['status'] = 'failure'
        self.assertEqual(self.summary()['status'], 'failure')
    def test_debug_only_is_missing(self):
        self.records.pop()
        self.assertEqual(self.summary()['status'], 'missing')
    def test_wrong_sha_branch_run_attempt_rejected(self):
        for key, value in [('head_sha', 'old'), ('branch', 'feature'), ('run_id', '11'), ('run_attempt', '1')]:
            with self.subTest(key=key):
                original = self.records[1][key]
                self.records[1][key] = value
                self.assertEqual(self.summary()['status'], 'missing')
                self.records[1][key] = original
    def test_legacy_is_not_success(self):
        self.records = [{'version': '1.2.3', 'status': 'success'}]
        self.assertEqual(self.summary()['status'], 'missing')
    def test_cancelled_run_not_success(self):
        self.run['conclusion'] = 'cancelled'
        self.assertEqual(self.summary()['status'], 'failure')
    def test_duplicate_configuration_fails(self):
        self.records.append(dict(self.records[0]))
        with self.assertRaises(ValueError): self.summary()
    def test_collection_failure_replaces_stale_success(self):
        with tempfile.TemporaryDirectory() as directory:
            previous = Path.cwd()
            try:
                os.chdir(directory)
                Path('.github/workflows').mkdir(parents=True)
                Path('.github/workflows/test-stm32-v1.2.3.yml').write_text('')
                Path('.github/test-results').mkdir()
                dest = Path('.github/test-results/1.2.3.json')
                dest.write_text('{"status":"success"}')
                with patch.dict(os.environ, {'GITHUB_REPOSITORY': 'owner/repo'}), patch.object(results, 'gh', side_effect=ValueError('bad response')):
                    results.collect('stm32')
                self.assertEqual(json.loads(dest.read_text())['collection_status'], 'collection-error')
                self.assertEqual(json.loads(dest.read_text())['status'], 'missing')
            finally: os.chdir(previous)

class PushAuthenticationTests(unittest.TestCase):
    def test_ephemeral_askpass_and_no_token_in_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            stub = Path(directory) / "git"
            capture = Path(directory) / "capture"
            stub.write_text("#!/usr/bin/env bash\nset -eu\nprintf '%s\\n' \"$@\" > \"$CAPTURE\"\n[[ $(\"$GIT_ASKPASS\" Username) == x-access-token ]]\n[[ $(\"$GIT_ASKPASS\" Password) == example-test-token ]]\nprintf '%s' \"$GIT_ASKPASS\" > \"$CAPTURE.path\"\n")
            stub.chmod(0o700)
            env = dict(os.environ, PATH=directory + os.pathsep + os.environ["PATH"],
                       GH_TOKEN="example-test-token", GITHUB_REPOSITORY="owner/repo", CAPTURE=str(capture))
            subprocess.run(["bash", str(ROOT/'.github/scripts/push-workflows.sh')], env=env, check=True)
            self.assertNotIn("example-test-token", capture.read_text())
            self.assertIn("https://github.com/owner/repo.git", capture.read_text())
            self.assertFalse(Path(Path(str(capture)+'.path').read_text()).exists())
    def test_push_failure_propagates_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as directory:
            stub = Path(directory) / "git"
            capture = Path(directory) / "askpass-path"
            stub.write_text('#!/usr/bin/env bash\nprintf "%s" "$GIT_ASKPASS" > "$CAPTURE"\nexit 17\n')
            stub.chmod(0o700)
            env = dict(os.environ, PATH=directory + os.pathsep + os.environ["PATH"],
                       GH_TOKEN="example-test-token", GITHUB_REPOSITORY="owner/repo", CAPTURE=str(capture))
            proc = subprocess.run(["bash", str(ROOT/'.github/scripts/push-workflows.sh')], env=env, capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(Path(capture.read_text()).exists())
            self.assertNotIn(b"example-test-token", proc.stdout + proc.stderr)
    def test_missing_token_fails(self):
        env = dict(os.environ); env.pop('GH_TOKEN', None)
        proc = subprocess.run(['bash', str(ROOT/'.github/scripts/push-workflows.sh')], env=env, capture_output=True)
        self.assertNotEqual(proc.returncode, 0)

class OutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.output = self.directory / 'app.elf'
        elf = bytearray(20); elf[:6] = b'\x7fELF\x01\x01'; elf[18:20] = struct.pack('<H', 40)
        self.output.write_bytes(elf)
    def tearDown(self): self.temp.cleanup()
    def test_arm_elf(self):
        self.assertEqual(outputs.verify('success', self.directory, self.output, True), self.output)
    def test_failed_build_with_artifact_fails(self):
        with self.assertRaises(ValueError): outputs.verify('failure', self.directory, self.output, True)
    def test_zero_length_fails(self):
        self.output.write_bytes(b'')
        with self.assertRaises(ValueError): outputs.verify('success', self.directory, self.output, True)
    def test_wrong_architecture_fails(self):
        self.output.write_bytes(b'not an ARM binary')
        with self.assertRaises(ValueError): outputs.verify('success', self.directory, self.output, True)
    def test_unique_ccs_fallback(self):
        self.assertEqual(outputs.verify('success', self.directory, self.directory/'expected.out'), self.output)
    def test_ambiguous_fallback_fails(self):
        (self.directory/'other.out').write_bytes(b'nonempty')
        with self.assertRaises(ValueError): outputs.verify('success', self.directory, self.directory/'expected.out')

class GeneratedWorkflowTests(unittest.TestCase):
    def test_result_refresh_uses_current_main_on_rerun(self):
        workflow = (ROOT/'.github/workflows/sync-test-results.yml').read_text()
        checkout = workflow.split('uses: actions/checkout@v6', 1)[1].split('      - name:', 1)[0]
        self.assertIn('ref: main', checkout)

    def test_generated_workflows_match_template(self):
        templates = list((ROOT/'.github/templates').glob('test-*-template.yml'))
        self.assertEqual(len(templates), 1)
        template = templates[0].read_text()
        prefix = 'ccs' if 'test-ccs-' in templates[0].name else 'stm32'
        for workflow in (ROOT/'.github/workflows').glob(f'test-{prefix}-v*.yml'):
            version = workflow.stem.split('-v', 1)[1]
            with self.subTest(version=version):
                self.assertEqual(workflow.read_text(), template.replace('{{VERSION}}', version))
    def test_clean_outputs_before_build(self):
        template = next((ROOT/'.github/templates').glob('test-*-template.yml')).read_text()
        self.assertLess(template.index('Remove previous'), template.index('- name: Build with'))
        self.assertIn("steps.build.outcome", template)
        self.assertNotIn("matrix.config == 'Debug'", template)
        self.assertIn(".github/workflows/test-", template)

if __name__ == '__main__': unittest.main()
