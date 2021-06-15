from fastapi    import HTTPException, status, Depends
from typing     import Optional

from calendar import timegm

from fastapi    import Query

from .exceptions import FilterByParameterError, MissedParameterError

from dateutil import parser as date_parser


def to_unix_time(dt):
    return timegm(dt.utctimetuple())


def process_report_params(remaining_params_processor=None, sortby_validator=None, filtering_validator=None):
    def inner(chunk_num:            int
                , chunk_size:       int
                # , schema:           Optional[str]=Query(None, max_length=4)
                , sort_by:          Optional[str]=Query(None, max_length=500)
                , filter_by:        Optional[str]=Query(None, max_length=500)
                , remaining_params: dict=Depends(remaining_params_processor or (lambda: {}))
    ):
        if sort_by:
            sortby_validator(sort_by)
        if filter_by:
            filtering_validator(filter_by)
        params = {
                # 'schema':       validate_schema_param(schema) if schema else None
                'chunk_num':    chunk_num
                , 'chunk_size': chunk_size
                , 'sort_by':    sort_by or None
                , 'filter_by':  filter_by or None
                # , **({k: v for k, v in zip(('sort_by', 'filter_by'), (sort_by, filter_by)) if v})
            }
        params.update(remaining_params)
        return params

    return inner



def parse_sort_fields(sortby_string: str, model_name: str=None, nullslast=True):
    sort_fields = sortby_string.split(',')

    sort_specs = []

    for direction_and_field in sort_fields:
        direction = direction_and_field[0]
        field     = direction_and_field[1:]

        sort_specs.append({
            **({'model': model_name} if model_name else {})
            , 'field': field
            , 'direction': 'desc' if direction == '-' else 'asc'
            , 'nullslast': nullslast
        })

    return sort_specs


def add_model_name(d: dict, model_name: str):
    return {**({'model': model_name} if model_name else {}), **d}


def parse_filter_fields(filterby_string: str, model_name: str=None, return_filter_specs=True): # validate sections mainly and return parsed data
    # Get string example: localhost:8000/api/incidents?chunk_num=1&chunk_size=4&sort_by=-insertdt,-name&filter_by=dtfields=startdt,enddt|itemfields=statuses,xatuses|items=INPGRS,RESLVD~INPGRS,RESLVD|textfields=name,desc|searchstring=a|startdt=2020-11-01T17:25:16.682Z|enddt=2021-01-10T17:25:16.682Z|dtfields=startdt,enddt
    # "~" (tilda) - is a separator in items
    """
        Example of filter specs:
        filter_specs = [
            {
                'and': [
                    {
                        'or': [
                            {
                                'and': [
                                    {'field': 'dtfield1', 'op': '<=', 'value': 'enddt'}
                                    , {'field': 'dtfield1', 'op': '>=', 'value': 'startdt'}
                                ]
                            }
                            , {
                                'and': [
                                    {'field': 'dtfield2', 'op': '<=', 'value': 'enddt'}
                                    , {'field': 'dtfield2', 'op': '>=', 'value': 'startdt'}
                                ]
                            }
                        ]
                    }
                    , {
                        'or': [
                            {'field': 'textfield1', 'op': 'like', 'value': 'searchstring'}
                            , {'field': 'textfield2', 'op': 'like', 'value': 'searchstring'}
                        ]
                    }
                    , {
                        'and': [
                            {
                                'or': [
                                    {'field': 'itemfiled1', 'op': '==', 'value': 'items1_1'}
                                    , {'field': 'itemfiled1', 'op': '==', 'value': 'items1_2'}
                                ]
                            }
                            , {
                                'or': [
                                    {'field': 'itemfield2', 'op': '==', 'value': 'items2_1'}
                                    , {'field': 'itemfield2', 'op': '==', 'value': 'items2_2'}
                                ]
                            }
                        ]
                    }
                ],
            }
        ]
    """
    SECTION_HEADERS = [
        'dtfields'
        , 'textfields'
        , 'itemfields'
        , 'items'
        , 'searchstring'
        , 'startdt'
        , 'enddt'
    ]

    LIST_SECTIONS = [
        'dtfields'
        , 'textfields'
        , 'itemfields'
        , 'items'
    ]

    D2_LIST_SECTIONS = [ # 2 dim list
        'items'
    ]

    section_dict = {
        'dtfields':         []
        , 'textfields':     []
        , 'itemfields':     []
        , 'items':          [] # it will be a 2d array
        , 'searchstring':   ''
        , 'startdt':        None
        , 'enddt':          None
    }


    sections = filterby_string.split('|')
    for section in sections:
        header_and_fields = section.split('=')
        header = header_and_fields[0]
        if header not in SECTION_HEADERS:
            raise FilterByParameterError(f"Section header value '{header}' is invalid. Allowed values: {SECTION_HEADERS}")
        if header in D2_LIST_SECTIONS:                                                          # if fields are in 2d array
            fields = [sublist.split(',') for sublist in header_and_fields[1].split('~')]        # sublists are separated by "~"
        else:                                                                                   # if fields are not in a 2d array
            fields = header_and_fields[1].split(',')

        section_dict[header] = fields[0] if (header not in LIST_SECTIONS) else fields # if element is not a list - make it a single element

    if (section_dict.get('startdt') or section_dict.get('enddt') or section_dict.get('dtfields'))\
        and not ((section_dict.get('startdt') and section_dict.get('dtfields')) or (section_dict.get('enddt') and section_dict.get('dtfields'))
    ):
        raise FilterByParameterError(f"Section 'dtfields' must be included with 'startdt' or 'enddt' or both")

    if (section_dict.get('searchstring') or section_dict.get('textfields')) and not (section_dict.get('searchstring') and section_dict.get('textfields')):
        raise FilterByParameterError(f"Both sections: 'searchstring' and 'textfields' must be included together")

    if (section_dict.get('items') or section_dict.get('itemfields')) and not (section_dict.get('items') and section_dict.get('itemfields')):
        raise FilterByParameterError(f"Both sections: 'itemfields' and 'items' must be included together")
    else:
        if (len(section_dict['items']) != len(section_dict['itemfields'])):
            raise FilterByParameterError(f"Sections 'itemfields' and 'items' must be of the same lenght")

    if not return_filter_specs:
        return section_dict

    dt_conditions       = {'or': []}
    text_conditions     = {'or': []}
    # status_conditions   = {'or': []}
    if len(section_dict['itemfields']) > 1:
        items_conditions   = {'and': []}
    else:
        items_conditions = None

    dt_conditions_populated     = False
    text_conditions_populated   = False
    items_conditions_populated  = False

    for dt_field in section_dict['dtfields']:
        if section_dict.get('startdt') and section_dict.get('enddt'):
            dt_conditions['or'].append({
                'and': [
                    add_model_name({'field': dt_field, 'op': '<=', 'value': date_parser.parse(section_dict['enddt'])}, model_name)         #!!! COMPARING DATES!
                    , add_model_name({'field': dt_field, 'op': '>=', 'value': date_parser.parse(section_dict['startdt'])}, model_name)
                ]
            })
        elif section_dict.get('startdt'):
            dt_conditions['or'].append(add_model_name({'field': dt_field, 'op': '>=', 'value': date_parser.parse(section_dict['startdt'])}, model_name))
        else:
            dt_conditions['or'].append(add_model_name({'field': dt_field, 'op': '<=', 'value': date_parser.parse(section_dict['enddt'])}, model_name))
        dt_conditions_populated = True

    for text_field in section_dict['textfields']:
        text_conditions['or'].append(
            add_model_name({'field': text_field, 'op': 'like', 'value': f"%{section_dict['searchstring']}%"}, model_name)  #!!! WILL LIKE WORK AS EXPECTED?
        )
        text_conditions_populated = True


    for item_field, items in zip(section_dict['itemfields'], section_dict['items']):
        item_conditions   = {'or': []}
        for item in items:
            item_conditions['or'].append(
                add_model_name({'field': item_field, 'op': '==', 'value': item}, model_name)
            )
        items_conditions_populated = True
        if items_conditions:                                            # if items_conditions = None, then no and condition is required
            items_conditions['and'].append(item_conditions)
        else:
            items_conditions = item_conditions


    if len([el for el in [items_conditions_populated, text_conditions_populated, dt_conditions_populated] if el]) <= 1: # if we hav onl one condition then no need for 'and' operator
        res = {
            **(dt_conditions if dt_conditions_populated else {})
            , **(text_conditions if text_conditions_populated else {})
            , **(items_conditions if items_conditions_populated else {})
        }
    else:
        res = {
            'and': [
                d for d, e in zip((dt_conditions, text_conditions, items_conditions,)
                                , (dt_conditions_populated, text_conditions_populated, items_conditions_populated,)
                ) if e
            ]
        }

    return res


def create_filterby_validator_tree(dt_fields:   list=None
                                , text_fields:  list=None
                                , item_fields:  list=None
                                , item_types:   list=None
                                , items_values: list=None # it can be [[], [a, b, c,,,], []]
                            ):
    if item_types or item_fields:
        if not (item_types and item_fields):
            raise Exception('"item_types" and "item_fileds" must be passed together')
        else:
            if len(item_types) != len(item_fields):
                raise Exception('"item_types" and "item_fileds" must be of the same lenght')
    if items_values and len(items_values) != len(item_fields):
        raise Exception('"items_values" and "item_fileds" must be of the same lenght')
    if items_values and not all([(not sublist or isinstance(sublist, list)) for sublist in items_values]):
        raise Exception('"items_values" must be a 2d array')
    return {
        'section_validator': {
            'dtfields': {
                'valid_values':     dt_fields or []
                , 'type_caster':    list
            }
            , 'textfields': {
                'valid_values':     text_fields or []
                , 'type_caster':    list
            }
            , 'itemfields': {
                'valid_values':     item_fields or []
                , 'type_caster':    list
            }
            , 'items': {
                'valid_values':     items_values or []
                , 'type_caster':    item_types   or []
                , 'order_by':       item_fields
                , 'relation':       'itemfields'
                , 'list':           True
            }
            , 'startdt': {
                'valid_values':     False
                , 'type_caster':    date_parser.parse
            }
            , 'enddt': {
                'valid_values':     False
                , 'type_caster':    date_parser.parse
            }
            , 'searchstring': {
                'valid_values':     False
                , 'type_caster':    str
            }
        }
    }


def filterby_validator(filterby_validator_tree: dict): # validate values in sections (for example, allowed fields or dates)
    def inner(filterby_string: str):
        STATUS_CODE = status.HTTP_422_UNPROCESSABLE_ENTITY
        DETAIL      = "'filter_by' parameter is ill-structured"
        HEADERS     = {'WWW-Authenticate': 'Bearer'}

        try:
            section_dict = parse_filter_fields(filterby_string, return_filter_specs=False)
        except FilterByParameterError as exc:
            raise HTTPException(
                status_code=STATUS_CODE
                , detail=DETAIL + '. ' + str(exc)
                , headers=HEADERS
            )
        except Exception as exc:
            raise HTTPException(
                status_code=STATUS_CODE
                , detail=DETAIL
                , headers=HEADERS
            )

        for section in section_dict:
            if not filterby_validator_tree['section_validator'].get(section):
                raise HTTPException(
                            status_code=STATUS_CODE
                            , detail=DETAIL + f". Invalid section '{section}'. Allowed sections: {list(filterby_validator_tree['section_validator'].keys())}"
                            , headers=HEADERS
                    )
            if filterby_validator_tree['section_validator'][section]['valid_values'] and not filterby_validator_tree['section_validator'][section].get('list'):
                # if not all([ (field in filterby_validator_tree['section_validator'][section]['valid_values']) for field in section_dict[section] ]):
                for field in section_dict[section]:
                    if field not in filterby_validator_tree['section_validator'][section]['valid_values']:
                        raise HTTPException(
                            status_code=STATUS_CODE
                            , detail=DETAIL + f". Field '{field}' is not valid. Allowed values: {filterby_validator_tree['section_validator'][section]['valid_values']}"
                            , headers=HEADERS
                        )
            if filterby_validator_tree['section_validator'][section]['type_caster'] and section_dict[section]:
                if filterby_validator_tree['section_validator'][section].get('list') and filterby_validator_tree['section_validator'][section]['list']: # some type_casters are lists of types that each array in the particular item field must conform to
                    # if filterby_validator_tree['section_validator'][section]['type_caster']:
                    try:
                        if filterby_validator_tree['section_validator'][section].get('order_by') and filterby_validator_tree['section_validator'][section]['order_by']:
                            field_typecasters = {fieldname: type_caster for fieldname, type_caster in zip(filterby_validator_tree['section_validator'][section]['order_by'], filterby_validator_tree['section_validator'][section]['type_caster'])}
                            relation_section  = filterby_validator_tree['section_validator'][section]['relation']
                            field_values      = {fieldname: values for fieldname, values in zip(section_dict[relation_section], section_dict[section])}

                            section_dict[section] = [[field_typecasters[fieldname](item) for item in values] for fieldname, values in field_values.items()]
                        else: # this branch is actually not in use at all
                            section_dict[section] = [[type_caster(item) for item in sublist] for sublist, type_caster in zip(section_dict[section], filterby_validator_tree['section_validator'][section]['type_caster'])] # we take that recdeived values are already in order
                    except Exception as exc:
                        raise HTTPException(
                            status_code=STATUS_CODE
                            , detail=DETAIL
                            , headers=HEADERS
                        )
                    if filterby_validator_tree['section_validator'][section]['valid_values']:
                        for items, valid_values in zip(section_dict[section], filterby_validator_tree['section_validator'][section]['valid_values']):
                            # if any([item not in valid_values for item in items if valid_values]):
                            for item in items:
                                if item not in valid_values:
                                    raise HTTPException(
                                        status_code=STATUS_CODE
                                        , detail=DETAIL + f". Item '{item}' is not valid. Allowed values: {valid_values}"
                                        , headers=HEADERS
                                    )
                else:
                    section_dict[section] = filterby_validator_tree['section_validator'][section]['type_caster'](section_dict[section])                 # type cast

    return inner


def sortby_fields_validator(valid_sort_fields: list):
    def inner(sortby_string: str):
        # from fastapi import HTTPException, status
        STATUS_CODE = status.HTTP_422_UNPROCESSABLE_ENTITY
        DETAIL      = "'sort_by' parameter is ill-structured"
        HEADERS     = {'WWW-Authenticate': 'Bearer'}

        try:
            sort_specs = parse_sort_fields(sortby_string)
        except:
            raise HTTPException(
                    status_code=STATUS_CODE
                    , detail=DETAIL
                    , headers=HEADERS
                )

        for row in sort_specs:
            if row['field'] not in valid_sort_fields:
                raise HTTPException(
                    status_code=STATUS_CODE
                    , detail=DETAIL + f". Field '{row['field']}' is not valid. Allowed values: {valid_sort_fields}"
                    , headers=HEADERS
                )

    return inner


def form_paginated_JSON(data: list
                        , total_rows: int=None
                        , chunk_num: int=None
                        , chunk_size: int=None
                        , name: str=None
                        , headers: list=None
                    ):
    return {
        **({'name':            name} if name is not None else {})
        , **({'headers':       headers} if name is not None else {})
        , 'data':              data
        , **({'total_entries': total_rows} if total_rows is not None else {})
        , **({'chunk_num':     chunk_num} if chunk_num is not None else {})
        , **({'chunk_size':    chunk_size} if chunk_size is not None else {})
    }
