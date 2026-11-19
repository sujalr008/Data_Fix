import json
import logging
import httpx
from typing import Dict, Any, List
from app.config import AI_API_KEY, AI_MODEL

logger = logging.getLogger('datafix.ai')

class AIService:
    @staticmethod
    def generate_insights(issues: List[Dict[str, Any]], row_count: int, columns: List[str]) -> Dict[str, Any]:
        # If API key is available, attempt Gemini call
        if AI_API_KEY:
            try:
                insights = AIService._call_gemini(issues, row_count, columns)
                if insights:
                    return insights
            except Exception as e:
                logger.warning(f'Gemini API call failed: {e}. Falling back to rule-based engine.')

        # Intelligent heuristic / rule-based AI engine
        return AIService._generate_heuristic_insights(issues, row_count, columns)

    @staticmethod
    def _call_gemini(issues: List[Dict[str, Any]], row_count: int, columns: List[str]) -> Dict[str, Any] | None:
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{AI_MODEL}:generateContent?key={AI_API_KEY}'
        prompt = (
            f'You are an expert data quality architect. Analyze this dataset profile:\n'
            f'- Total Rows: {row_count}\n'
            f'- Columns: {columns}\n'
            f'- Detected Issues: {json.dumps(issues)}\n\n'
            f'Respond in valid JSON only with keys: "aiInsights" (string), "rootCauses" (list of strings), '
            f'"riskAssessment" (string), and "priorityOrder" (list of strings).'
        )
        payload = {
            'contents': [{'parts': [{'text': prompt}]}]
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data['candidates'][0]['content']['parts'][0]['text']
                # Clean json markers if present
                clean_text = text.strip().removeprefix('`json').removeprefix('`').removesuffix('`').strip()
                return json.loads(clean_text)
        return None

    @staticmethod
    def _generate_heuristic_insights(issues: List[Dict[str, Any]], row_count: int, columns: List[str]) -> Dict[str, Any]:
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        high_issues = [i for i in issues if i.get('severity') == 'high']
        missing_issues = [i for i in issues if i.get('type') == 'missing_values']
        dup_issues = [i for i in issues if i.get('type') == 'duplicates']
        format_issues = [i for i in issues if i.get('type') == 'format_errors']
        outlier_issues = [i for i in issues if i.get('type') == 'outliers']

        # Root causes
        root_causes = []
        if missing_issues:
            fields = ', '.join([i['field'] for i in missing_issues[:3]])
            root_causes.append(f'Optional form inputs or upstream data ingestion drops in fields: {fields}')
        if dup_issues:
            root_causes.append('Repeated batch imports or absent database primary key constraints allowing duplicate rows')
        if format_issues:
            root_causes.append('Heterogeneous data collection sources with inconsistent client-side formatting and validation')
        if outlier_issues:
            root_causes.append('Unvalidated user inputs, sensor glitches, or unit conversion anomalies causing extreme values')
        if not root_causes:
            root_causes.append('General data collection variability; no structural pipeline anomalies identified')

        # Risk assessment
        if critical_issues:
            crit_fields = ', '.join([i['field'] for i in critical_issues[:2]])
            risk_assessment = f'Critical — High failure probability for downstream analytics and joins due to severe issues in {crit_fields}.'
        elif high_issues:
            risk_assessment = f'High — Multiple fields require remediation to prevent skew in statistical models and reporting.'
        elif issues:
            risk_assessment = 'Moderate — Minor formatting and null anomalies present with low operational risk.'
        else:
            risk_assessment = 'Low — Dataset demonstrates high data integrity with minimal risk.'

        # Priority order
        priority_order = []
        for i in critical_issues:
            priority_order.append(f'Urgent: Resolve {i["type"].replace("_", " ")} in "{i["field"]}" ({i["affectedCount"]} affected)')
        for i in high_issues:
            if i not in critical_issues:
                priority_order.append(f'High Priority: Address {i["type"].replace("_", " ")} in "{i["field"]}"')
        for i in issues:
            if i not in critical_issues and i not in high_issues and len(priority_order) < 4:
                priority_order.append(f'Standard: Standardise {i["field"]} ({i.get("suggestedFix", "fix format")})')
        if not priority_order:
            priority_order.append('Maintain periodic schema validation routines')

        # AI Insights overview
        ai_insights = (
            f'The dataset analysis identified {len(issues)} data quality issue(s) across {len(columns)} columns and {row_count} rows. '
            f'Primary points of concern involve {", ".join([i["type"].replace("_", " ") for i in (critical_issues or issues)[:2]])}. '
            'Automated repair strategies are recommended to normalize formats, impute missing values, and guarantee downstream pipeline consistency.'
        )

        return {
            'aiInsights': ai_insights,
            'rootCauses': root_causes,
            'riskAssessment': risk_assessment,
            'priorityOrder': priority_order
        }
