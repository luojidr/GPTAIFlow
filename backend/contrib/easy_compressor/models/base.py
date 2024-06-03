from flask import current_app
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import load_only

db = current_app.extensions["sqlalchemy"]

__all__ = ["BaseModel", "db"]


class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {
        "extend_existing": True
    }

    @classmethod
    def query_selected_fields(cls, *criterion, fields: list[str]):
        # with_entities: 元祖
        # options + load_only: 对象
        col_fields = [getattr(cls, name) for name in fields]
        query = cls.query.options(load_only(*col_fields)).filter(*criterion)
        return query.all()

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        fields = cls.fields()
        values = {key: val for key, val in kwargs.items() if key in fields}

        instance = cls(**values)
        return instance.save()

    @classmethod
    def insert_bulk_objects(cls, objects):
        db.session.bulk_save_objects(objects)
        db.session.commit()

        return objects

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if commit:
            return self.save()
        return self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit: bool = True) -> None:
        """Remove the record from the database."""
        db.session.delete(self)
        if commit:
            return db.session.commit()
        return

    @classmethod
    def fields(cls):
        # cls.__table__.columns | cls.__mapper__.columns
        columns = []
        for c in cls.__table__.columns:
            columns.append(c.name)

        return columns

    def to_dict(self, include_relations=False):
        result = {}
        for key in self.__mapper__.columns.keys():
            result[key] = getattr(self, key)

        if include_relations:
            for relationship in self.__mapper__.relationships:
                related_obj = getattr(self, relationship.key)
                if isinstance(related_obj, list):  # 一对多或多对多关系
                    result[relationship.key] = [i.to_dict() for i in related_obj]
                elif related_obj is not None:  # 外键、一对一关系
                    result[relationship.key] = related_obj.to_dict()  # 假设相关对象也有 `.to_dict()` 方法

        return result

    @classmethod
    def sql(cls, query):
        return query.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True})

    @classmethod
    def table_name(cls):
        return cls.__tablename__
