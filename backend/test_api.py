import sys
import io
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from starlette.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_pipeline():
    print('\n==================== STARTING END-TO-END API TESTS ====================')

    # 1. Health check
    print('\n[1/8] Testing GET /api/health...')
    resp = client.get('/api/health')
    assert resp.status_code == 200, f'Expected 200, got {resp.status_code}'
    health_data = resp.json()
    assert health_data.get('success') is True
    print('  ✓ Health check passed:', health_data.get('message'))

    # 2. File Upload
    print('\n[2/8] Testing POST /api/upload...')
    sample_csv = (
        'id,name,email,age,join_date\n'
        '1, John Doe ,john@example.com,29,2023-01-15\n'
        '2,Jane Smith,jane.smith@invalid,25,2023/02/20\n'
        '3,Bob Brown,,150,2023-03-10\n'
        '3,Bob Brown,,150,2023-03-10\n'
        '4,Alice Ray,alice@example.com,24,2023-04-05\n'
    )
    files = {'file': ('test_data.csv', io.BytesIO(sample_csv.encode('utf-8')), 'text/csv')}
    resp = client.post('/api/upload', files=files)
    assert resp.status_code == 200, f'Upload failed: {resp.text}'
    upload_data = resp.json()
    assert upload_data['success'] is True
    u_data = upload_data['data']
    session_id = u_data['sessionId']
    print('  ✓ Upload passed! Session ID:', session_id)
    print('  ✓ Quality Score:', u_data['qualityScore'])
    print('  ✓ Issues found:', len(u_data['issues']))

    # 3. Retrieve Analysis
    print('\n[3/8] Testing GET /api/analysis/' + session_id + '...')
    resp = client.get('/api/analysis/' + session_id)
    assert resp.status_code == 200, f'Analysis fetch failed: {resp.text}'
    analysis_data = resp.json()
    assert analysis_data['success'] is True
    assert analysis_data['data']['sessionId'] == session_id
    print('  ✓ Analysis retrieved successfully.')

    # 4. AI Insights
    print('\n[4/8] Testing POST /api/analysis/' + session_id + '/ai-insights...')
    resp = client.post('/api/analysis/' + session_id + '/ai-insights')
    assert resp.status_code == 200, f'AI insights failed: {resp.text}'
    insights_data = resp.json()
    assert insights_data['success'] is True
    assert 'rootCauses' in insights_data['data']
    assert 'riskAssessment' in insights_data['data']
    assert 'priorityOrder' in insights_data['data']
    print('  ✓ AI Insights generated:')
    print('    - Risk Assessment:', insights_data['data']['riskAssessment'])
    print('    - Root Causes:', insights_data['data']['rootCauses'])
    print('    - Priority Order:', insights_data['data']['priorityOrder'])

    # 5. Apply Repair
    print('\n[5/8] Testing POST /api/repair/' + session_id + '...')
    repair_payload = {
        'repairOptions': {
            'fixMissing': True,
            'removeDuplicates': True,
            'fixFormats': True,
            'fixOutliers': True
        }
    }
    resp = client.post('/api/repair/' + session_id, json=repair_payload)
    assert resp.status_code == 200, f'Repair failed: {resp.text}'
    repair_data = resp.json()
    assert repair_data['success'] is True
    rep_res = repair_data['data']
    print('  ✓ Repair applied: count =', rep_res['repairCount'], ', new quality score =', rep_res['newQualityScore'])
    print('  ✓ AI Explanation:', rep_res['aiExplanation'])

    # 6. Diff Check
    print('\n[6/8] Testing GET /api/repair/' + session_id + '/diff...')
    resp = client.get('/api/repair/' + session_id + '/diff')
    assert resp.status_code == 200, f'Diff failed: {resp.text}'
    diff_data = resp.json()
    assert diff_data['success'] is True
    print('  ✓ Total changes detected in diff:', diff_data['data']['totalChanges'])
    for change in diff_data['data']['changes'][:3]:
        print('    - Row', change['rowIndex'], 'field', change['field'], ':', change['original'], '->', change['fixed'])

    # 7. Downloads (CSV and XLSX)
    print('\n[7/8] Testing GET /api/download/' + session_id + '...')
    resp_csv = client.get('/api/download/' + session_id + '?format=csv')
    assert resp_csv.status_code == 200
    assert 'text/csv' in resp_csv.headers['content-type']
    assert len(resp_csv.content) > 0
    print('  ✓ CSV download verified (bytes received:', len(resp_csv.content), ')')

    resp_xlsx = client.get('/api/download/' + session_id + '?format=xlsx')
    assert resp_xlsx.status_code == 200
    assert len(resp_xlsx.content) > 0
    print('  ✓ XLSX download verified (bytes received:', len(resp_xlsx.content), ')')

    # 8. Report
    print('\n[8/8] Testing GET /api/report/' + session_id + '...')
    resp_report = client.get('/api/report/' + session_id)
    assert resp_report.status_code == 200, f'Report fetch failed: {resp_report.text}'
    report_json = resp_report.json()
    assert report_json['success'] is True
    rep_data = report_json['data']
    print('  ✓ Comprehensive Report verified:')
    print('    - Quality Score:', rep_data['qualityScore'])
    print('    - Total Issues:', rep_data['totalIssues'])
    print('    - Issues by Type:', rep_data['issuesByType'])
    print('    - Column Analysis entries:', len(rep_data['columnAnalysis']))
    print('    - Repair Summary:', rep_data['repairSummary'])
    print('    - Timeline:', rep_data['timeline'])

    print('\n==================== ALL 8 API CONTRACT TESTS PASSED! ====================\n')

if __name__ == '__main__':
    test_full_pipeline()
