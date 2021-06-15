import sqlalchemy_filters


def get_query_models(query):            # oatch sqlalchemy_filters broken function
    """Get models from query.

    :param query:
        A :class:`sqlalchemy.orm.Query` instance.

    :returns:
        A dictionary with all the models included in the query.
    """
    models = [col_desc['entity'] for col_desc in query.column_descriptions]
    models.extend(mapper.class_ for mapper in query._join_entities)

    print()
    print()
    print()
    print('osu!')
    print()
    print(models)
    print()
    print(len(models))
    print()
    print()
    print()
    print()
    print()
    print()

    # account also query.select_from entities
    if (
        hasattr(query, '_select_from_entity') and
        (query._select_from_entity is not None)
    ):
        model_class = (
            query._select_from_entity.class_
            if isinstance(query._select_from_entity, sqlalchemy_filters.models.Mapper)  # sqlalchemy>=1.1
            else query._select_from_entity  # sqlalchemy==1.0
        )
        if model_class not in models:
            models.append(model_class)

    return {model.__name__: model for model in models if model} #! added if
