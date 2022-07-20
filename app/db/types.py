import sqlalchemy.types as types


class Priority(types.TypeDecorator):

    impl = types.String

    def __init__(self, **kwargs) -> None:
        self.priorities = ["LOW", "NORMAL", "HIGH", "VERY HIGH"]
        super(Priority, self).__init__(**kwargs)

    def process_bind_param(self, value, dialect) -> str:
        return value if value in self.priorities else None

    def process_result_value(self, value, dialect) -> str:
        return value if value in self.priorities else None
