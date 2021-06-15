# from datetime       import date, datetime, timedelta
# from sqlalchemy.orm import Session

# from ..models import    reports_med as reports_med_model_controller
# from ..models import    incidents   as incidents_model_controller
# from ...common import   utils       as common_utils

# from ..utils import serve_report, serve_report

# from sqlalchemy         import and_
# from sqlalchemy         import case
# from sqlalchemy         import func


# SI3000_MASK = '44..H0W0_'

# def form_max_load_files_query(db: Session, is_routing: int=0, get_si3000: bool=False):
#     subquery = db.query(incidents_model_controller.Incident, incidents_model_controller.Station)\
#                 .join(incidents_model_controller.Status, incidents_model_controller.Incident.status == incidents_model_controller.Status.status)\
#                 .join(incidents_model_controller.Station\
#                     , and_(incidents_model_controller.Incident.id == incidents_model_controller.Station.incident_id
#                             , incidents_model_controller.Incident.enddt.isnot(None))
#                 ).subquery()

#     query = db.query(
#         reports_med_model_controller.MedMaxLoadFilesDatesView.ftid
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.ftname
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.stationname
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.fdate
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.fileregdt
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.maxcalldate
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.mincalldate
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.lastloaddiff
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.lastloaddifflegacy
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.lastfileid
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.isrouting
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.alloweddiff
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.hostip
#         , reports_med_model_controller.MedMaxLoadFilesDatesView.contactperson
#         , case([(subquery.columns.station_ft_id.is_(None), 0)], else_=1).label('hasactincident')
#     ).join(subquery, and_(subquery.columns.station_ft_id.like('%' + reports_med_model_controller.MedMaxLoadFilesDatesView.ftid + '%')) # left outer join
#                         , isouter=True)\
#     .filter( (reports_med_model_controller.MedMaxLoadFilesDatesView.isrouting == is_routing) if not get_si3000 else (reports_med_model_controller.MedMaxLoadFilesDatesView.ftid.like(SI3000_MASK)) )

#     return query


# def db_get_max_load_cdr_files_dt(db: Session): # No pagination needed for this report
#     query   = form_max_load_files_query(db, 0)
#     data    = query.all()

#     return data, len(data)


# def db_get_max_load_files_dt_si3000(db: Session):
#     query   = form_max_load_files_query(db, get_si3000=True)
#     data    = query.all()

#     return data, len(data)


# def db_get_check_traff_by_internal_tgs(db: Session, month: datetime):
#     query   = db.query(reports_med_model_controller.MedCheckTrafficByInternalTGsView).filter(func.trunc(reports_med_model_controller.MedCheckTrafficByInternalTGsView.datetraf, 'MM') == func.trunc(month, 'MM'))
#     data    = query.all()

#     return data, len(data)


# @serve_report
# def db_get_max_load_route_files_dt(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     sort_specs   = None if not sort_by else common_utils.parse_sort_fields(sort_by)
#     filter_specs = None if not filter_by else common_utils.parse_filter_fields(filter_by)

#     query = form_max_load_files_query(db, 1)

#     return query, sort_specs, filter_specs


# @serve_report
# def db_get_file_load_exc(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     sort_specs   = None if not sort_by else common_utils.parse_sort_fields(sort_by)
#     filter_specs = None if not filter_by else common_utils.parse_filter_fields(filter_by)

#     query = db.query(reports_med_model_controller.MedFileLoadExceptionsView)

#     return query, sort_specs, filter_specs


# @serve_report
# def db_get_file_load_exc_si3000(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     sort_specs   = None if not sort_by else common_utils.parse_sort_fields(sort_by)
#     filter_specs = None

#     query = db.query(reports_med_model_controller.MedFileLoadExceptionsView).filter(reports_med_model_controller.MedFileLoadExceptionsView.ftid.like(SI3000_MASK))

#     return query, sort_specs, filter_specs


# @serve_report
# def db_get_loaded_rows_diff(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     sort_specs   = None if not sort_by else common_utils.parse_sort_fields(sort_by)
#     filter_specs = None if not filter_by else common_utils.parse_filter_fields(filter_by)

#     query = db.query(reports_med_model_controller.MedLoadedRowsDiffView)

#     return query, sort_specs, filter_specs


# @serve_report
# def db_get_loaded_rows_diff_si3000(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     sort_specs   = None if not sort_by else common_utils.parse_sort_fields(sort_by)
#     filter_specs = None

#     query = db.query(reports_med_model_controller.MedLoadedRowsDiffView).filter(reports_med_model_controller.MedLoadedRowsDiffView.ftid.like(SI3000_MASK))

#     return query, sort_specs, filter_specs


# @serve_report
# def db_get_incorrect_seq(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     sort_specs   = None if not sort_by else common_utils.parse_sort_fields(sort_by)
#     filter_specs = None if not filter_by else common_utils.parse_filter_fields(filter_by)

#     query= db.query(reports_med_model_controller.MedIncorrectSequencesView)

#     return query, sort_specs, filter_specs


# @serve_report
# def db_get_incorrect_seq_si3000(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     sort_specs   = None if not sort_by else common_utils.parse_sort_fields(sort_by)
#     filter_specs = None

#     query= db.query(reports_med_model_controller.MedIncorrectSequencesView).filter(reports_med_model_controller.MedIncorrectSequencesView.ftid.like(SI3000_MASK))

#     return query, sort_specs, filter_specs


# def preprocess_avg_file_qty_report_data(data: list):
#     res = []
#     today_dt = date.today()
#     today_dt = datetime(today_dt.year, today_dt.month, today_dt.day)
#     dates = [ today_dt - timedelta(days=6)
#             , today_dt - timedelta(days=5)
#             , today_dt - timedelta(days=4)
#             , today_dt - timedelta(days=3)
#             , today_dt - timedelta(days=2)
#             , today_dt - timedelta(days=1)
#             , today_dt
#         ]

#     for row in data:
#         res.append({
#             'ftid':             row.ftid
#             , 'diff':           row.diff
#             , 'ftctrl':         row.ftctrl
#             , 'isrouting':      row.isrouting
#             , 'numsoffiles':    [row.filestodayminus6days
#                                 , row.filestodayminus5days
#                                 , row.filestodayminus4days
#                                 , row.filestodayminus3days
#                                 , row.filestodayminus2days
#                                 , row.filestodayminus1days
#                                 , row.filestoday
#                             ]
#             , 'dates':          dates
#         })

#     return res



# def db_get_avg_file_qty_diff(db: Session, is_routing: bool, sort_by: str=None, filter_by: str=None):
#     sort_specs   = None if not sort_by else common_utils.parse_sort_fields(sort_by)
#     filter_specs = None if not filter_by else common_utils.parse_filter_fields(filter_by)

#     query= db.query(reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView)\
#                 .filter((reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView.isrouting == 1) if is_routing
#                         else (reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView.isrouting == 0))

#     return query, sort_specs, filter_specs


# def db_get_avg_file_qty_diff_si3000(db: Session, is_routing: bool, sort_by: str=None, filter_by: str=None):
#     sort_specs   = None if not sort_by else common_utils.parse_sort_fields(sort_by)
#     filter_specs = None if not filter_by else common_utils.parse_filter_fields(filter_by)

#     query= db.query(reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView)\
#                 .filter(and_(reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView.ftid.like(SI3000_MASK)
#                             ,   ((reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView.isrouting == 1) if is_routing
#                                     else (reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView.isrouting == 0)
#                             ))
#                     )

#     return query, sort_specs, filter_specs



# def db_get_avg_file_qty_diff_stations(db: Session, is_routing: bool):
#     data = db.query(reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView)\
#                 .distinct(reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView.ftid)\
#                 .filter((reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView.isrouting == 1) if is_routing
#                         else (reports_med_model_controller.MedAverageLoadedFilesQuantityDiffView.isrouting == 0)).all()

#     data = [row.ftid for row in data]
#     data.sort()

#     return data


# @serve_report
# def db_get_avg_cdr_file_qty_diff(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     return db_get_avg_file_qty_diff(db, is_routing=False, sort_by=sort_by, filter_by=filter_by)


# @serve_report
# def db_get_avg_route_file_qty_diff(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     return db_get_avg_file_qty_diff(db, is_routing=True, sort_by=sort_by, filter_by=filter_by)


# @serve_report
# def db_get_avg_cdr_file_qty_diff_si3000(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     return db_get_avg_file_qty_diff_si3000(db, is_routing=False, sort_by=sort_by, filter_by=filter_by)


# @serve_report
# def db_get_avg_route_file_qty_diff_si3000(db: Session, page_number: int, page_size: int, sort_by: str=None, filter_by: str=None):
#     return db_get_avg_file_qty_diff_si3000(db, is_routing=True, sort_by=sort_by, filter_by=filter_by)



# def db_get_avg_cdr_file_qty_dif_stations(db: Session):
#     return db_get_avg_file_qty_diff_stations(db, is_routing=False)


# def db_get_avg_route_file_qty_dif_stations(db: Session):
#     return db_get_avg_file_qty_diff_stations(db, is_routing=True)
