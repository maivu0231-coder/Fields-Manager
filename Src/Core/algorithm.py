from typing import Any, Callable, List, Optional

def binary_search(sorted_list:List[Any], target: Any) -> int:
    left = 0
    right = len(sorted_list)-1
    
    while left <= right:
        mid = (left + right) // 2
        value = sorted_list[mid]
        if value == target:
            return mid
        elif value < target:
            left = mid + 1
        else:
            right = mid - 1      

def merge_sort(items: List[Any], key: Callable[[Any], Any]) -> List[Any]:
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left_half = merge_sort(items[:mid], key)
    right_half = merge_sort(items[mid:], key)
    return _merge(left_half, right_half, key)
def _merge(left: List[Any], right: List[Any], key: Callable[[Any],Any]) -> List[Any]:
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    while i < len(left):
        result.append(left[i])
        i += 1
    while j < len(right):
        result.append(right[j])
        j += 1
        
    return result

def linear_search(items: List[Any], target: Any, key: Callable[[Any], Any]) -> Optional[Any]:
    for item in items:
        if key(item) == target:
            return item
    return None
        