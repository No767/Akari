from typing import Dict, List, Union


def formatOptions(rows: Union[List[Dict[str, str]], None]) -> str:
    """_summary_

    Args:
        rows (Union[List[Dict[str, str]], None]): _description_

    Returns:
        str: _description_
    """
    if rows is None or len(rows) == 0:
        return "Tag not found"

    names = "\n".join([row["name"] for row in rows])
    return f"Tag not found. Did you mean:\n{names}"
