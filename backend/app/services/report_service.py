import pandas as pd
from typing import Dict, Any

class ReportService:
    @staticmethod
    def generate_report(session: Dict[str, Any]) -> Dict[str, Any]:
        issues = session.get('issues', [])
        columns = session.get('columns', [])
        original_data = session.get('originalData', [])
        repaired_data = session.get('repairedData')
        repairs = session.get('repairs', [])
        
        # Issues by type
        issues_by_type = {
            'missing_values': 0,
            'duplicates': 0,
            'format_errors': 0,
            'outliers': 0
        }
        for i in issues:
            itype = i.get('type')
            if itype in issues_by_type:
                issues_by_type[itype] += i.get('affectedCount', 1)
            else:
                issues_by_type[itype] = i.get('affectedCount', 1)

        # Issues by severity
        issues_by_severity = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        for i in issues:
            sev = i.get('severity', 'low')
            if sev in issues_by_severity:
                issues_by_severity[sev] += 1
            else:
                issues_by_severity[sev] = 1

        # Column Analysis
        df = pd.DataFrame(original_data) if original_data else pd.DataFrame()
        total_rows = len(df)
        column_analysis = []
        for col in columns:
            col_issues = sum(i.get('affectedCount', 1) for i in issues if i.get('field') == col)
            if col in df.columns and total_rows > 0:
                valid_count = df[col].dropna().apply(lambda x: str(x).strip() not in ['', 'null', 'nan', 'none', 'n/a', 'N/A']).sum()
                completeness = round(float((valid_count / total_rows) * 100), 1)
                dtype = str(df[col].dtype)
                col_type = 'numeric' if 'int' in dtype or 'float' in dtype else ('datetime' if 'datetime' in dtype else 'string')
            else:
                completeness = 100.0
                col_type = 'string'

            column_analysis.append({
                'column': col,
                'issues': int(col_issues),
                'completeness': completeness,
                'type': col_type
            })

        # Repair Summary
        original_row_count = session.get('rowCount', len(original_data))
        repaired_row_count = len(repaired_data) if repaired_data is not None else original_row_count

        repair_summary = {
            'totalRepairs': len(repairs),
            'repairedRowCount': repaired_row_count,
            'originalRowCount': original_row_count
        }

        # Quality score
        quality_score = session.get('qualityScore', 100)

        # Timeline
        timeline = {
            'uploadedAt': session.get('createdAt', '2026-11-19T10:00:00.000Z'),
            'analysedAt': session.get('updatedAt', '2026-11-19T10:00:02.000Z'),
            'repairedAt': session.get('repairedAt')
        }

        return {
            'qualityScore': quality_score,
            'totalIssues': len(issues),
            'issuesByType': issues_by_type,
            'issuesBySeverity': issues_by_severity,
            'columnAnalysis': column_analysis,
            'repairSummary': repair_summary,
            'aiInsights': session.get('aiInsights', 'Dataset analysis completed successfully.'),
            'timeline': timeline
        }
