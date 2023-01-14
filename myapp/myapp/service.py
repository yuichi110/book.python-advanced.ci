from myapp.repository import Repository


class IndexService:
    def __init__(self, repository: Repository):
        self._repository = repository

    def add_item(self, item_name):
        self._repository.insert_item(item_name)

    def get_items(self):
        original_items = self._repository.get_items()
        items = [item[1] for item in original_items]
        return items
