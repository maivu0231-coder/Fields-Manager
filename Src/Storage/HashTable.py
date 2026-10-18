from typing import Any, List, Optional, Tuple


class HashNode:

    def __init__(self, key: str, value: Any) -> None:
        self.key = str(key)
        self.value = value


class CustomHashTable:


    def __init__(self, initial_capacity: int = 16, load_factor_threshold: float = 0.75) -> None:
        self.capacity = max(4, initial_capacity)
        self.size = 0
        self.load_factor_threshold = load_factor_threshold
        self.buckets: List[List[HashNode]] = [[] for _ in range(self.capacity)]

    def _hash(self, key: str) -> int:
        key_str = str(key)
        hash_val = 0
        prime = 31
        for char in key_str:
            hash_val = (hash_val * prime + ord(char)) % self.capacity
        return hash_val

    def _rehash(self) -> None:
        old_buckets = self.buckets
        self.capacity *= 2
        self.size = 0
        self.buckets = [[] for _ in range(self.capacity)]

        for bucket in old_buckets:
            for node in bucket:
                self.put(node.key, node.value)

    def put(self, key: str, value: Any) -> None:
        if (self.size + 1) / self.capacity > self.load_factor_threshold:
            self._rehash()

        index = self._hash(key)
        bucket = self.buckets[index]

        for node in bucket:
            if node.key == str(key):
                node.value = value  # Cập nhật nếu key đã tồn tại
                return

        bucket.append(HashNode(str(key), value))
        self.size += 1

    def get(self, key: str) -> Optional[Any]:
        index = self._hash(key)
        bucket = self.buckets[index]

        for node in bucket:
            if node.key == str(key):
                return node.value
        return None

    def remove(self, key: str) -> bool:

        index = self._hash(key)
        bucket = self.buckets[index]

        for i, node in enumerate(bucket):
            if node.key == str(key):
                bucket.pop(i)
                self.size -= 1
                return True
        return False

    def contains(self, key: str) -> bool:
        return self.get(key) is not None

    def values(self) -> List[Any]:
        result = []
        for bucket in self.buckets:
            for node in bucket:
                result.append(node.value)
        return result

    def items(self) -> List[Tuple[str, Any]]:
        result = []
        for bucket in self.buckets:
            for node in bucket:
                result.append((node.key, node.value))
        return result