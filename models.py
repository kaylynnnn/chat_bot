from donphan import Table, Column, SQLType


__all__ = ('Prefix',)


class Prefix(Table):
    guild: Column[SQLType.BigInt] = Column(unique=True, nullable=False)
    prefix: Column[SQLType.Text] = Column(unique=True, nullable=False)