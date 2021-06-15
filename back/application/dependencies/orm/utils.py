from os import getenv

from sqlalchemy.orm     import Session
from sqlalchemy_filters import apply_pagination, apply_sort, apply_filters
from functools          import wraps

from .db_config     import sessions


class DBGetter:
    def __init__(self, whatdb):
        self.sessions   = sessions
        self.whatdb     = whatdb

    def __call__(self):
        try:
            db = self.sessions[self.whatdb]()
            yield db
        except:
            raise
        finally:
            db.close()


def paginate_query(query, page_number: str, page_size: str):
    res, pagination = apply_pagination(query, page_number=page_number, page_size=page_size)

    page_size, page_number, num_pages, total_rows = pagination

    return res.all(), total_rows


def apply_specs(func, db: Session, page_number: int, page_size: int, *args, sort_by: str=None, filter_by: str=None, **kwargs):
    MAX_QUERY_RES_LENGTH = getenv('MAX_QUERY_RES_LENGTH')
    if MAX_QUERY_RES_LENGTH and page_size > int(MAX_QUERY_RES_LENGTH):
        print(f'Limiting query result set to the top level result number bound: {int(MAX_QUERY_RES_LENGTH)}. Asked: {page_size}')
        page_size = int(MAX_QUERY_RES_LENGTH)

    query, sort_specs, filter_specs = func(db
                                            , page_number
                                            , page_size
                                            , *args
                                            , **({'sort_by': sort_by} if sort_by else {})
                                            , **({'filter_by': filter_by} if filter_by else {})
                                            , **kwargs
                                    )

    if filter_specs:
        query = apply_filters(query, filter_specs)
    if sort_specs:
        query = apply_sort(query, sort_specs)

    return paginate_query(query, page_number, page_size)


def serve_report(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return apply_specs(func, *args, **kwargs)

    return wrapper

