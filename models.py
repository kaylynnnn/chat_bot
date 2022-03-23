from donphan import Table, Column, SQLType


__all__ = ('Prefix',)


class Guilds(Table):
    guild: Column[SQLType.BigInt] = Column(primary_key=True, nullable=False)
    owoify: Column[SQLType.Boolean] = Column(default=False)


class Prefix(Table):
    guild: Column[SQLType.BigInt] = Column(unique=True, nullable=False, references=Guilds.guild)
    prefix: Column[SQLType.Text] = Column(unique=True, nullable=False)