# core/age_utils.py

import re
import pandas as pd

def parse_age_to_tuple(label: str, remove_prefix: bool = True) -> tuple[str, int, int, int]:
    """
    年齢ラベルを正規化し、(ラベル, min, max, median) を返すタプル形式。
    85歳以上については、maxを90歳と仮に決める
    """
    label = str(label).translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    if remove_prefix:
        label = label.replace("年齢階層_", "")

    match_open = re.match(r"^(\d+)[^0-9]*$", label)
    if match_open:
        a_min = int(match_open.group(1))
        a_max = 90
        a_med = (a_min + a_max) // 2
        return f"{a_min}+", a_min, a_max, a_med

    match = re.match(r"(\d+)[^0-9]+(\d+)", label)
    if match:
        a_min = int(match.group(1))
        a_max = int(match.group(2))
        a_med = (a_min + a_max) // 2
        return f"{a_min}-{a_max}", a_min, a_max, a_med

    return label, None, None, None

