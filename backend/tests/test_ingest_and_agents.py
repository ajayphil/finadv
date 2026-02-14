import os
from fastapi.testclient import TestClient
from app.main import app
import app.agents as agents

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


def test_upload_csv_and_analyze(tmp_path, monkeypatch):
    # ensure agent LLM returns a predictable response
    monkeypatch.setattr(agents, '_call_llm_with_context', lambda s, u, r=None: 'MOCKED_ANALYSIS')

    csv_path = os.path.join(os.path.dirname(__file__), '..', 'sample_data', 'sample_finances.csv')
    with open(csv_path, 'rb') as f:
        files = {'file': ('sample_finances.csv', f, 'text/csv')}
        r = client.post('/ingest/upload_csv', files=files, data={'doc_id': 'testdoc'})
    assert r.status_code == 200
    assert r.json().get('rows') > 0

    payload = {
        'user': {
            'income': 5000,
            'recurring_spending': 2500,
            'discretionary_spending': 300,
            'debts': [
                {'name': 'Visa', 'balance': 1200, 'rate': 18.5, 'min_payment': 36}
            ],
            'savings': 500
        }
    }
    r2 = client.post('/analyze/debt', json=payload)
    assert r2.status_code == 200
    assert 'summary' in r2.json()
    assert 'MOCKED_ANALYSIS' in r2.json()['summary']
*** End Patch