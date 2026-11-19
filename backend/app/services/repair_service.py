import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from app.services.quality_service import DataQualityService
from app.services.parser_service import sanitize_records

class RepairService:
    @staticmethod
    def apply_repairs(
        records: List[Dict[str, Any]],
        columns: List[str],
        options: Dict[str, bool]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int, int, str]:
        if not records:
            return [], [], 100, 0, 'No data to repair.'

        df = pd.DataFrame(records)
        repair_log = []
        applied_categories = []

        # 1. Remove Duplicates
        if options.get('removeDuplicates', True):
            initial_count = len(df)
            dup_indices = df[df.duplicated()].index.tolist()
            if dup_indices:
                for idx in dup_indices:
                    repair_log.append({
                        'action': 'removed_duplicate',
                        'rowIndex': int(idx)
                    })
                df = df.drop_duplicates().reset_index(drop=True)
                removed_dups = initial_count - len(df)
                applied_categories.append(f'{removed_dups} duplicate rows removed')

        # 2. Fix Formats (trim whitespace, lower emails, ISO dates)
        if options.get('fixFormats', True):
            format_fix_count = 0
            for col in columns:
                if col not in df.columns:
                    continue
                # Trim whitespace
                for idx, val in enumerate(df[col]):
                    if isinstance(val, str) and (val.startswith(' ') or val.endswith(' ')):
                        trimmed = val.strip()
                        df.at[idx, col] = trimmed
                        repair_log.append({
                            'action': 'standardised_format',
                            'field': col,
                            'rowIndex': idx,
                            'value': trimmed
                        })
                        format_fix_count += 1

                # Emails to lowercase
                if 'email' in col.lower():
                    for idx, val in enumerate(df[col]):
                        if isinstance(val, str) and val.lower() not in ['n/a', 'none', 'null', 'nan']:
                            cleaned_email = val.strip().lower()
                            if cleaned_email != val:
                                df.at[idx, col] = cleaned_email
                                repair_log.append({
                                    'action': 'standardised_format',
                                    'field': col,
                                    'rowIndex': idx,
                                    'value': cleaned_email
                                })
                                format_fix_count += 1

                # Dates to ISO YYYY-MM-DD
                if any(k in col.lower() for k in ['date', 'dob', 'created_at']):
                    for idx, val in enumerate(df[col]):
                        if pd.notnull(val) and str(val).strip() != '':
                            try:
                                parsed_date = pd.to_datetime(val)
                                iso_date = parsed_date.strftime('%Y-%m-%d')
                                if str(val) != iso_date:
                                    df.at[idx, col] = iso_date
                                    repair_log.append({
                                        'action': 'standardised_format',
                                        'field': col,
                                        'rowIndex': idx,
                                        'value': iso_date
                                    })
                                    format_fix_count += 1
                            except Exception:
                                pass
            if format_fix_count > 0:
                applied_categories.append(f'{format_fix_count} format inconsistencies standardised')

        # 3. Fix Missing Values
        if options.get('fixMissing', True):
            missing_fix_count = 0
            for col in columns:
                if col not in df.columns:
                    continue
                # Check if column is numeric
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                is_numeric = numeric_series.notnull().sum() > (len(df) * 0.5)

                if is_numeric:
                    median_val = float(numeric_series.median()) if numeric_series.notnull().sum() > 0 else 0
                    if float(median_val).is_integer():
                        median_val = int(median_val)
                    for idx, val in enumerate(df[col]):
                        if pd.isna(val) or val in ['', 'null', 'nan', 'none', 'n/a', 'NULL', 'NaN', 'None', 'N/A']:
                            df.at[idx, col] = median_val
                            repair_log.append({
                                'action': 'imputed',
                                'field': col,
                                'rowIndex': idx,
                                'value': median_val
                            })
                            missing_fix_count += 1
                else:
                    # Non-numeric imputation
                    placeholder = 'N/A'
                    for idx, val in enumerate(df[col]):
                        if pd.isna(val) or val in ['', 'null', 'nan', 'none', 'n/a', 'NULL', 'NaN', 'None', 'N/A']:
                            df.at[idx, col] = placeholder
                            repair_log.append({
                                'action': 'imputed',
                                'field': col,
                                'rowIndex': idx,
                                'value': placeholder
                            })
                            missing_fix_count += 1
            if missing_fix_count > 0:
                applied_categories.append(f'{missing_fix_count} missing values imputed')

        # 4. Fix Outliers
        if options.get('fixOutliers', False):
            outlier_fix_count = 0
            for col in columns:
                if col not in df.columns or any(k in col.lower() for k in ['id', 'zip', 'code', 'phone', 'year']):
                    continue
                num_series = pd.to_numeric(df[col], errors='coerce')
                valid_nums = num_series.dropna()
                if len(valid_nums) >= 4:
                    q1 = valid_nums.quantile(0.25)
                    q3 = valid_nums.quantile(0.75)
                    iqr = q3 - q1
                    if iqr > 0:
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        for idx, val in enumerate(num_series):
                            if pd.notnull(val):
                                if val < lower_bound:
                                    clipped = round(lower_bound, 2)
                                    df.at[idx, col] = clipped
                                    repair_log.append({
                                        'action': 'clipped_outlier',
                                        'field': col,
                                        'rowIndex': idx,
                                        'value': clipped
                                    })
                                    outlier_fix_count += 1
                                elif val > upper_bound:
                                    clipped = round(upper_bound, 2)
                                    df.at[idx, col] = clipped
                                    repair_log.append({
                                        'action': 'clipped_outlier',
                                        'field': col,
                                        'rowIndex': idx,
                                        'value': clipped
                                    })
                                    outlier_fix_count += 1
            if outlier_fix_count > 0:
                applied_categories.append(f'{outlier_fix_count} statistical outliers clipped')

        # Clean NaN to None for JSON serialization
        repaired_records = df.where(pd.notnull(df), None).to_dict(orient='records')
        new_quality_score, remaining_issues = DataQualityService.analyze(repaired_records, columns)

        if applied_categories:
            ai_explanation = f'{len(repair_log)} repairs applied successfully. ' + '; '.join(applied_categories) + '.'
        else:
            ai_explanation = 'Dataset analyzed with no repairs requested or needed.'

        return sanitize_records(repaired_records), repair_log, new_quality_score, len(remaining_issues), ai_explanation
