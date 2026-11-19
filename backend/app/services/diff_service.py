import math
import pandas as pd
from typing import List, Dict, Any
from app.services.parser_service import sanitize_records

def clean_val(val):
    if val is None:
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    if pd.isna(val):
        return None
    return val

class DiffService:
    @staticmethod
    def calculate_diff(
        original: List[Dict[str, Any]],
        repaired: List[Dict[str, Any]],
        columns: List[str]
    ) -> Dict[str, Any]:
        clean_orig = sanitize_records(original)
        clean_rep = sanitize_records(repaired)
        changes = []
        min_len = min(len(clean_orig), len(clean_rep))

        for idx in range(min_len):
            orig_row = clean_orig[idx]
            rep_row = clean_rep[idx]
            for col in columns:
                v_orig = clean_val(orig_row.get(col))
                v_rep = clean_val(rep_row.get(col))

                is_changed = False
                if (v_orig is None or v_orig == '') and (v_rep is not None and v_rep != ''):
                    is_changed = True
                elif (v_orig is not None and v_orig != '') and (v_rep is None or v_rep == ''):
                    is_changed = True
                elif v_orig != v_rep:
                    is_changed = True

                if is_changed:
                    changes.append({
                        'rowIndex': idx,
                        'field': col,
                        'original': v_orig,
                        'fixed': v_rep
                    })

        if len(clean_rep) < len(clean_orig):
            for idx in range(len(clean_rep), len(clean_orig)):
                changes.append({
                    'rowIndex': idx,
                    'field': 'entire_row',
                    'original': clean_orig[idx],
                    'fixed': '[REMOVED_DUPLICATE]'
                })

        return {
            'original': clean_orig,
            'repaired': clean_rep,
            'changes': changes,
            'totalChanges': len(changes)
        }
