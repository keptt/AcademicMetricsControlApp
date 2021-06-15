from datetime       import datetime
from sqlalchemy.orm import Session
from typing         import List
from fastapi        import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from ..dependencies.orm.utils                   import DBGetter
from ..dependencies.pydantic.models.incidents   import Incident
from ..dependencies.admin.auth                  import check_if_admin
from ..dependencies.common                      import utils as common_utils
from ..dependencies.common                      import xlsx

from ..dependencies.orm.routines       import reports_med  as reports_med_controller
from ..dependencies.pydantic.models    import reports_med  as reports_med_pydantic_model_controller

from ..dependencies.orm                import utils as orm_utils


router = APIRouter(
    prefix='/reports/med',
    dependencies=[Depends(check_if_admin)],
)



INCORRECT_SEQ_MED_HEADERS = [
            {'text':   'seq',           'value': 'seq'}
            , {'text': 'ft_id',         'value': 'ftid'}
            , {'text': 'f_id',          'value': 'fid'}
            , {'text': 'f_date',        'value': 'fdate'}
            , {'text': 'file_reg_dt',   'value': 'fileregdt'}
            , {'text': 'table_rec_cnt', 'value': 'tablereccnt'}
            , {'text': 'f_rec_cnt',     'value': 'freccnt'}
            , {'text': 'f_status',      'value': 'fstatus'}
            , {'text': 'max_call_date', 'value': 'maxcalldate'}
            , {'text': 'min_call_date', 'value': 'mincalldate'}
            , {'text': 'min_sn',        'value': 'minsn'}
            , {'text': 'max_sn',        'value': 'maxsn'}
            , {'text': 'seq_diff',      'value': 'seqdiff'}
        ]


FILE_LOAD_EXC_MED_HEADERS = [
            {'text':   'ft_id',         'value': 'ftid'}
            , {'text': 'f_id',          'value': 'fid'}
            , {'text': 'cnt',           'value': 'cnt'}
            , {'text': 'msg',           'value': 'msg'}
            , {'text': 'f_status',      'value': 'fstatus'}
            , {'text': 'f_date',        'value': 'fdate'}
            , {'text': 'min_call_date', 'value': 'mincalldate'}
            , {'text': 'max_call_date', 'value': 'maxcalldate'}
            , {'text': 'file_reg_dt',   'value': 'fileregdt'}
        ]


LOADED_ROWS_DIFF_MED_HEADERS = [
            {'text':   'diff_rows',     'value': 'diffrows'}
            , {'text': 'diff_minus_exc','value': 'diffminusexc'}
            , {'text': 'is_exc',        'value': 'isexc'}
            , {'text': 'ft_id',         'value': 'ftid'}
            , {'text': 'f_id',          'value': 'fid'}
            , {'text': 'f_date',        'value': 'fdate'}
            , {'text': 'f_status',      'value': 'fstatus'}
            , {'text': 'f_rec_cnt',     'value': 'freccnt'}
            , {'text': 'table_rec_cnt', 'value': 'tablereccnt'}
            , {'text': 'min_call_date', 'value': 'mincalldate'}
            , {'text': 'max_call_date', 'value': 'maxcalldate'}
            , {'text': 'file_reg_dt',   'value': 'fileregdt'}
        ]


MAX_LOAD_FILES_MED_HEADERS = [
            {'text':   'ft_id',                 'value': 'ftid'}
            , {'text': 'ft_name',               'value': 'ftname'}
            , {'text': 'station_name',          'value': 'stationname'}
            , {'text': 'f_date',                'value': 'fdate'}
            , {'text': 'file_reg_dt',           'value': 'fileregdt'}
            , {'text': 'max_call_date',         'value': 'maxcalldate'}
            , {'text': 'min_call_date',         'value': 'mincalldate'}
            , {'text': 'last_load_diff',        'value': 'lastloaddiff'}
            , {'text': 'last_load_diff_legacy', 'value': 'lastloaddifflegacy'}
            , {'text': 'last_file_id',          'value': 'lastfileid'}
            , {'text': 'host_ip',               'value': 'hostip'}
            , {'text': 'contact_person',        'value': 'contactperson'}
            , {'text': 'has_act_incident',      'value': 'hasactincident'}
            # , {'text': 'isrouting',  'value': 'isrouting'}
        ]


AVG_FILE_QTY_DIFF_MED_HEADERS = [
    {'text':   'ft_id',         'value': 'ftid'}
    , {'text': 'nums_of_files', 'value': 'numsoffiles'}
    , {'text': 'dates',         'value': 'dates'}
    , {'text': 'diff',          'value': 'diff'}
    , {'text': 'ft_ctrl',       'value': 'ftctrl'}
    , {'text': 'is_routing',    'value': 'isrouting'}
]


MAX_LOAD_ROUTE_FILES_DT_VALID_FIELDS = [
    'ftid'
    , 'ftname'
    , 'stationname'
    , 'fdate'
    , 'fileregdt'
    , 'maxcalldate'
    , 'mincalldate'
    , 'lastloaddiff'
    , 'lastloaddifflegacy'
    , 'lastfileid'
    , 'alloweddiff'
    # , 'isissue'
    , 'hasactincident'
]

LOADED_ROWS_DIFF_VALID_FIELDS = [
    'diffrows'
    , 'diffminusexc'
    , 'isexc'
    , 'ftid'
    , 'fid'
    , 'fdate'
    , 'fstatus'
    , 'freccnt'
    , 'tablereccnt'
    , 'mincalldate'
    , 'maxcalldate'
    , 'fileregdt'
]


FILE_LOAD_EXCEPTIONS_VALID_FIELDS = [
    'ftid'
    , 'fid'
    , 'cnt'
    , 'err'
    , 'msg'
    , 'fstatus'
    , 'fdate'
    , 'mincalldate'
    , 'maxcalldate'
    , 'fileregdt'
]

INCORRECT_SEQUENCES_VALID_FIELDS = [
    'seq'
    , 'ftid'
    , 'fid'
    , 'fdate'
    , 'fileregdt'
    , 'tablereccnt'
    , 'freccnt'
    , 'fstatus'
    , 'maxcalldate'
    , 'mincalldate'
    , 'minsn'
    , 'maxsn'
    , 'seqdiff'
]


AVG_FILE_QTY_DIFF_VALID_FIELDS = [
    'ftid'
    , 'diff'
    , 'ftctrl'
    , 'isrouting'
]


@router.get('/max-load-cdr-files-dt-med', response_model=reports_med_pydantic_model_controller.MedMaxLoadFileDatesReportData)
def get_max_load_cdr_files_dt(db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_max_load_cdr_files_dt(db)

    name    = 'lastLoadedCDRFilesReportMed'
    headers = MAX_LOAD_FILES_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
        )


@router.get('/max-load-cdr-files-dt-med/si3000', response_model=reports_med_pydantic_model_controller.MedMaxLoadFileDatesReportData)
def get_max_load_cdr_files_dt_si3000(db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_max_load_files_dt_si3000(db)

    name    = 'lastLoadedCDRFilesReportMed'
    headers = MAX_LOAD_FILES_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
        )


MAX_LOAD_ROUTE_FILES_DT_FILTER_TREE_VALIDATOR = common_utils.create_filterby_validator_tree(
                                                                    item_fields=['lastfileid', 'ftid']
                                                                    , item_types=[int, str]
                                                                    , dt_fields=['maxcalldate', 'mincalldate', 'fileregdt', 'fdate']
                                                                    , text_fields=['ftname', 'stationname', 'ftid']
                                                                )


@router.get('/max-load-route-files-dt-med', response_model=reports_med_pydantic_model_controller.MedMaxLoadFileDatesReportData)
def get_max_load_route_files_dt(params: dict=Depends(common_utils.process_report_params(None, common_utils.sortby_fields_validator(MAX_LOAD_ROUTE_FILES_DT_VALID_FIELDS), common_utils.filterby_validator(MAX_LOAD_ROUTE_FILES_DT_FILTER_TREE_VALIDATOR))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_max_load_route_files_dt(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])

    name    = 'lastLoadedRouteFilesReportMed'
    headers = MAX_LOAD_FILES_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )


LOADED_ROWS_DIFF_FILTER_TREE_VALIDATOR = common_utils.create_filterby_validator_tree(
                                                                    item_fields=['fid', 'fstatus']
                                                                    , item_types=[int, int]
                                                                    , dt_fields=['maxcalldate', 'mincalldate', 'fileregdt', 'fdate']
                                                                    , text_fields=['ftid']
                                                                )


@router.get('/loaded-rows-diff-med', response_model=reports_med_pydantic_model_controller.MedLoadedRowsDiffReportData)
def get_loaded_rows_diff(params: dict=Depends(common_utils.process_report_params(None, common_utils.sortby_fields_validator(LOADED_ROWS_DIFF_VALID_FIELDS), common_utils.filterby_validator(LOADED_ROWS_DIFF_FILTER_TREE_VALIDATOR))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_loaded_rows_diff(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])

    name    = 'loadedRowsDiffReportMed'
    headers = LOADED_ROWS_DIFF_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )


@router.get('/loaded-rows-diff-med/si3000', response_model=reports_med_pydantic_model_controller.MedLoadedRowsDiffReportData)
def get_loaded_rows_diff_si3000(params: dict=Depends(common_utils.process_report_params(sortby_validator=common_utils.sortby_fields_validator(LOADED_ROWS_DIFF_VALID_FIELDS))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_loaded_rows_diff_si3000(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])

    name    = 'loadedRowsDiffReportMedSi3000'
    headers = LOADED_ROWS_DIFF_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )


FILE_LOAD_EXCEPTIONS_FILTER_TREE_VALIDATOR = common_utils.create_filterby_validator_tree(
                                                                    item_fields=['fid', 'fstatus', 'ftid']
                                                                    , item_types=[int, int, str]
                                                                    , dt_fields=['maxcalldate', 'mincalldate', 'fileregdt', 'fdate']
                                                                    , text_fields=['ftid', 'msg']
                                                                )

@router.get('/file-load-exc-med', response_model=reports_med_pydantic_model_controller.MedFileLoadExcReportData)
def get_file_load_exc(params: dict=Depends(common_utils.process_report_params(None, common_utils.sortby_fields_validator(FILE_LOAD_EXCEPTIONS_VALID_FIELDS), common_utils.filterby_validator(FILE_LOAD_EXCEPTIONS_FILTER_TREE_VALIDATOR))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_file_load_exc(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])

    name    = 'fileLoadExceptionsReportMed'
    headers = FILE_LOAD_EXC_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )


@router.get('/file-load-exc-med/si3000', response_model=reports_med_pydantic_model_controller.MedFileLoadExcReportData)
def get_file_load_exc_si3000(params: dict=Depends(common_utils.process_report_params(sortby_validator=common_utils.sortby_fields_validator(FILE_LOAD_EXCEPTIONS_VALID_FIELDS))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_file_load_exc_si3000(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])

    name    = 'fileLoadExceptionsReportMedSi3000'
    headers = FILE_LOAD_EXC_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )


INCORRECT_SEQUENCES_FILTER_TREE_VALIDATOR = common_utils.create_filterby_validator_tree(
                                                                    item_fields=['fid', 'fstatus']
                                                                    , item_types=[int, int]
                                                                    , dt_fields=['maxcalldate', 'mincalldate', 'fileregdt', 'fdate']
                                                                    , text_fields=['ftid']
                                                                )


@router.get('/incorrect-seq-med', response_model=reports_med_pydantic_model_controller.MedIncorrectSeqReportData)
def get_incorrect_seq(params: dict=Depends(common_utils.process_report_params(None, common_utils.sortby_fields_validator(INCORRECT_SEQUENCES_VALID_FIELDS), common_utils.filterby_validator(INCORRECT_SEQUENCES_FILTER_TREE_VALIDATOR))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_incorrect_seq(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])

    name    = 'incorrectSequencesReportMed'
    headers = INCORRECT_SEQ_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )


@router.get('/incorrect-seq-med/si3000', response_model=reports_med_pydantic_model_controller.MedIncorrectSeqReportData)
def get_incorrect_seq_si3000(params: dict=Depends(common_utils.process_report_params(sortby_validator=common_utils.sortby_fields_validator(INCORRECT_SEQUENCES_VALID_FIELDS))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_incorrect_seq_si3000(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])

    name    = 'incorrectSequencesReportMedSi3000'
    headers = INCORRECT_SEQ_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )



@router.get('/avg-cdr-file-qty-diff-med/stations', response_model=reports_med_pydantic_model_controller.StationsReply)
def get_avg_cdr_file_qty_diff_stattions(db: Session=Depends(DBGetter('beezer'))):
    return {
        'stations': reports_med_controller.db_get_avg_cdr_file_qty_dif_stations(db)
    }


AVG_FILE_QTY_DIFF_FILTER_TREE_VALIDATOR = common_utils.create_filterby_validator_tree(
                                                                    item_fields=['ftid']
                                                                    , item_types=[str]
                                                                    , text_fields=['ftid']
                                                                )


@router.get('/avg-cdr-file-qty-diff-med', response_model=reports_med_pydantic_model_controller.MedAverageLoadedFilesQuantityDiffData)
def get_avg_cdr_file_qty_diff(params: dict=Depends(common_utils.process_report_params(None, common_utils.sortby_fields_validator(AVG_FILE_QTY_DIFF_VALID_FIELDS), common_utils.filterby_validator(AVG_FILE_QTY_DIFF_FILTER_TREE_VALIDATOR))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_avg_cdr_file_qty_diff(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])
    rows             = reports_med_controller.preprocess_avg_file_qty_report_data(rows)

    name    = 'avgCDRFileQtyDiffReportMed'
    headers = AVG_FILE_QTY_DIFF_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )


@router.get('/avg-route-file-qty-diff-med/stations', response_model=reports_med_pydantic_model_controller.StationsReply)
def get_avg_route_file_qty_diff_stattions(db: Session=Depends(DBGetter('beezer'))):
    return {
        'stations': reports_med_controller.db_get_avg_route_file_qty_dif_stations(db)
    }


@router.get('/avg-route-file-qty-diff-med', response_model=reports_med_pydantic_model_controller.MedAverageLoadedFilesQuantityDiffData)
def get_avg_route_file_qty_diff(params: dict=Depends(common_utils.process_report_params(None, common_utils.sortby_fields_validator(AVG_FILE_QTY_DIFF_VALID_FIELDS), common_utils.filterby_validator(AVG_FILE_QTY_DIFF_FILTER_TREE_VALIDATOR))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_avg_route_file_qty_diff(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])
    rows             = reports_med_controller.preprocess_avg_file_qty_report_data(rows)

    name    = 'avgRouteFileQtyDiffReportMed'
    headers = AVG_FILE_QTY_DIFF_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )


@router.get('/avg-cdr-file-qty-diff-med/si3000', response_model=reports_med_pydantic_model_controller.MedAverageLoadedFilesQuantityDiffData)
def get_avg_cdr_file_qty_diff(params: dict=Depends(common_utils.process_report_params(None, common_utils.sortby_fields_validator(AVG_FILE_QTY_DIFF_VALID_FIELDS), common_utils.filterby_validator(AVG_FILE_QTY_DIFF_FILTER_TREE_VALIDATOR))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_avg_cdr_file_qty_diff_si3000(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])
    rows             = reports_med_controller.preprocess_avg_file_qty_report_data(rows)

    name    = 'avgCDRFileQtyDiffReportMed'
    headers = AVG_FILE_QTY_DIFF_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )


@router.get('/avg-route-file-qty-diff-med/si3000', response_model=reports_med_pydantic_model_controller.MedAverageLoadedFilesQuantityDiffData)
def get_avg_route_file_qty_diff(params: dict=Depends(common_utils.process_report_params(None, common_utils.sortby_fields_validator(AVG_FILE_QTY_DIFF_VALID_FIELDS), common_utils.filterby_validator(AVG_FILE_QTY_DIFF_FILTER_TREE_VALIDATOR))), db: Session=Depends(DBGetter('beezer'))):
    rows, total_rows = reports_med_controller.db_get_avg_route_file_qty_diff_si3000(db, params['chunk_num'], params['chunk_size'], params['sort_by'], params['filter_by'])
    rows             = reports_med_controller.preprocess_avg_file_qty_report_data(rows)

    name    = 'avgRouteFileQtyDiffReportMed'
    headers = AVG_FILE_QTY_DIFF_MED_HEADERS

    return common_utils.form_paginated_JSON(
            name=name
            , headers=headers
            , data=rows
            , total_rows=total_rows
            , chunk_num=params['chunk_num']
            , chunk_size=params['chunk_size']
        )


# @router.get('/check-traff-by-internal-tgs-med', response_model=reports_med_pydantic_model_controller.MedCheckTrafficByInternalTGsReportData)
@router.get('/check-traff-by-internal-tgs-med', response_description='xlsx check-traff-by-internal-tgs-med report')
def get_check_traff_by_internal_tgs(month: datetime, db: Session=Depends(DBGetter('beezer'))):
    rows, num_of_rows = reports_med_controller.db_get_check_traff_by_internal_tgs(db, month)

    name    = 'checkTraffByInternalTGsMed.xlsx'
    headers = [
            {'text':   'date_traf',           'value': 'datetraf'}
            , {'text': 'station_id1',         'value': 'stationid1'}
            , {'text': 'trk_grp_in1',         'value': 'trkgrpin1'}
            , {'text': 'i_calls_success',     'value': 'icallssuccess'}
            , {'text': 'i_calls_all',         'value': 'icallsall'}
            , {'text': 'i_duration',          'value': 'iduration'}
            , {'text': 'station_id2',         'value': 'stationid2'}
            , {'text': 'trk_grp_in2',         'value': 'trkgrpin2'}
            , {'text': 'o_calls_success',     'value': 'ocallssuccess'}
            , {'text': 'o_calls_all',         'value': 'ocallsall'}
            , {'text': 'o_duration',          'value': 'oduration'}
            , {'text': 'diff_calls_success',  'value': 'diffcallssuccess'}
            , {'text': 'diff_duration',       'value': 'diffduration'}
            , {'text': 'diff_calls_all',      'value': 'diffcallsall'}
        ]

    rows = [dict(reports_med_pydantic_model_controller.MedCheckTrafficByInternalTGsReportRow.from_orm(row)) for row in rows]
    xlsx_bytes = xlsx.create_xlsx_bytes(headers, rows)

    http_headers = {
        'Content-Disposition': f'attachment; filename="{name}"'
    }

    return StreamingResponse(xlsx_bytes, headers=http_headers)
