import re
import math
import pandas as pd
from typing import List, Dict, Any, Tuple

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

class DataQualityService:
    @staticmethod
    def analyze(records: List[Dict[str, Any]], columns: List[str]) -> Tuple[int, List[Dict[str, Any]]]:
        if not records:
            return 100, []

        df = pd.DataFrame(records)
        row_count = len(df)
        issues = []
        total_penalty = 0

        # 1. Missing Values Detection
        for col in columns:
            series = df[col] if col in df.columns else pd.Series([None] * row_count)
            missing_mask = series.isna() | series.isin(['', 'null', 'nan', 'none', 'n/a', 'na', 'NULL', 'NaN', 'None', 'N/A'])
            missing_count = int(missing_mask.sum())
            if missing_count > 0:
                pct = (missing_count / row_count) * 100
                is_key_field = any(k in col.lower() for k in ['id', 'email', 'name', 'phone', 'key'])
                if pct > 15 or (is_key_field and pct > 5):
                    severity = 'critical'
                    total_penalty += min(25, pct * 0.8)
                elif pct > 5:
                    severity = 'high'
                    total_penalty += min(15, pct * 0.5)
                else:
                    severity = 'medium'
                    total_penalty += min(10, pct * 0.3)

                suggested_fix = 'Impute with placeholder or drop rows' if is_key_field else 'Impute with median or placeholder'
                issues.append({
                    'type': 'missing_values',
                    'field': col,
                    'severity': severity,
                    'affectedCount': missing_count,
                    'suggestedFix': suggested_fix
                })

        # 2. Duplicate Detection
        dup_mask = df.duplicated()
        duplicate_count = int(dup_mask.sum())
        if duplicate_count > 0:
            dup_pct = (duplicate_count / row_count) * 100
            severity = 'critical' if dup_pct > 10 else ('high' if duplicate_count > 2 else 'medium')
            total_penalty += min(20, dup_pct * 1.0)
            issues.append({
                'type': 'duplicates',
                'field': 'all_columns',
                'severity': severity,
                'affectedCount': duplicate_count,
                'suggestedFix': 'Deduplicate exact-match records'
            })

        # 3. Format Errors (Email, Whitespace, Dates)
        for col in columns:
            if col not in df.columns:
                continue
            series = df[col].dropna()
            str_series = series.astype(str).str.strip()

            # Email check
            if 'email' in col.lower():
                invalid_emails = [val for val in str_series if val and val.lower() not in ['n/a', 'none', 'null', 'nan'] and not EMAIL_REGEX.match(val)]
                if len(invalid_emails) > 0:
                    severity = 'critical' if len(invalid_emails) > 3 else 'high'
                    total_penalty += min(15, len(invalid_emails) * 2)
                    issues.append({
                        'type': 'format_errors',
                        'field': col,
                        'severity': severity,
                        'affectedCount': len(invalid_emails),
                        'suggestedFix': 'Standardise email syntax and remove invalid characters'
                    })

            # Date check
            elif any(k in col.lower() for k in ['date', 'time', 'dob', 'created_at']):
                date_format_errors = 0
                for val in str_series:
                    if not val or val.lower() in ['n/a', 'none', 'null', 'nan']:
                        continue
                    try:
                        pd.to_datetime(val)
                    except Exception:
                        date_format_errors += 1
                if date_format_errors > 0:
                    total_penalty += min(15, date_format_errors * 2)
                    issues.append({
                        'type': 'format_errors',
                        'field': col,
                        'severity': 'high' if date_format_errors > 3 else 'medium',
                        'affectedCount': date_format_errors,
                        'suggestedFix': 'Standardise date to ISO 8601 (YYYY-MM-DD)'
                    })

            # Untrimmed whitespace
            whitespace_count = int((df[col].astype(str) != df[col].astype(str).str.strip()).sum())
            if whitespace_count > 0:
                issues.append({
                    'type': 'format_errors',
                    'field': col,
                    'severity': 'low',
                    'affectedCount': whitespace_count,
                    'suggestedFix': 'Trim leading and trailing whitespace'
                })
                total_penalty += min(5, whitespace_count * 0.5)

        # 4. Outliers Detection (Numeric columns)
        for col in columns:
            if col not in df.columns:
                continue
            numeric_vals = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(numeric_vals) >= 4 and not any(k in col.lower() for k in ['id', 'zip', 'code', 'phone', 'year']):
                q1 = numeric_vals.quantile(0.25)
                q3 = numeric_vals.quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    outliers = numeric_vals[(numeric_vals < lower_bound) | (numeric_vals > upper_bound)]
                    outlier_count = len(outliers)
                    if outlier_count > 0:
                        severity = 'high' if outlier_count > 5 else 'medium'
                        total_penalty += min(10, outlier_count * 1.5)
                        issues.append({
                            'type': 'outliers',
                            'field': col,
                            'severity': severity,
                            'affectedCount': outlier_count,
                            'suggestedFix': f'Clip values outside range [{round(lower_bound, 2)}, {round(upper_bound, 2)}]'
                        })

        quality_score = max(5, min(100, int(round(100 - total_penalty))))
        return quality_score, issues
