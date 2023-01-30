from typing import Optional, Union


def CommandKeyBuilder(
    prefix: Optional[str] = "cache",
    namespace: Optional[str] = "akari",
    id: Union[Optional[str], Optional[int]] = None,
    command: Optional[str] = None,
) -> str:
    """A key builder for commands

    Args:
        prefix (Optional[str], optional): Prefix of the key. Defaults to "cache".
        namespace (Optional[str], optional): Namespace of the key. Defaults to "akari".
        id (Optional[int], optional): Discord User or Guild ID. Defaults to None.
        command (Optional[str], optional): Slash Command Name. Defaults to None.

    Returns:
        str: The key stored in Redis
    """
    return f"{prefix}:{namespace}:{id}:{command}"
