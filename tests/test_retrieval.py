import json
import tempfile
import unittest
from pathlib import Path

from groundedops.retrieval import Passage, Retriever, load_passages, tokenize

ROOT = Path(__file__).resolve().parents[1]


class RetrievalTests(unittest.TestCase):
    def test_tokenization(self):
        self.assertEqual(tokenize('How do WEBHOOK signatures verify?'), ['webhook', 'signatures', 'verify'])

    def test_citation_ids_and_source(self):
        r = Retriever.from_folder(ROOT / 'knowledge')
        hits = r.search('How do we prevent webhook duplicate events?')
        self.assertTrue(any(x.source == 'integrations.md' for x in hits))
        self.assertTrue(all('#' in x.id for x in hits))

    def test_unknown_returns_no_hits(self):
        r = Retriever.from_folder(ROOT / 'knowledge')
        self.assertEqual(r.search('astronaut zebras astrophysics'), [])

    def test_rank_is_deterministic(self):
        r = Retriever.from_folder(ROOT / 'knowledge')
        self.assertEqual(r.search('integration outage'), r.search('integration outage'))

    def test_invalid_k(self):
        with self.assertRaises(ValueError):
            Retriever([]).search('hi', top_k=0)

    def test_csv_input(self):
        r = Retriever.from_folder(ROOT / 'knowledge')
        self.assertTrue(any('DEMO-101' in p.text for p in r.passages))

    def test_index_ignores_hidden_and_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / 'policy.md').write_text('Policy owner approval', encoding='utf-8')
            (path / '.env').write_text('SOME_API_KEY=secret', encoding='utf-8')
            (path / 'irrelevant.py').write_text('secret key', encoding='utf-8')
            paths = load_passages(path)
            self.assertEqual(len(paths), 1)
            self.assertEqual(paths[0].source, 'policy.md')

    def test_limit_large_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'large.md').write_text('a' * 300_001)
            with self.assertRaises(ValueError):
                load_passages(Path(tmp))

    def test_chunk_long_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'long.md').write_text(' '.join('item' + str(i) for i in range(250)))
            p = load_passages(Path(tmp))
            self.assertGreater(len(p), 2)
            self.assertTrue(all(len(x.text.split()) <= 105 for x in p))


if __name__ == '__main__':
    unittest.main()
