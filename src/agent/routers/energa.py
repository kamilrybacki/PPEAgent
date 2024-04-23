"""
    This module provides a FastAPI router that is responsible for handling the requests related to fetching the energy consumption data from the Energa MojLicznik app.
"""
import datetime
import functools
import typing

import fastapi
import fastapi.responses
import requests

import agent.utils.consts
import agent.utils.retry

MEASUREMENTS_ROUTER = fastapi.APIRouter()


class EnergaMeasurementData(typing.TypedDict):
    """
        This is a typed dictionary that represents the measurements for a given timestamp i.e. how datapoints are represented by Energa app.
    """
    tm: str  # timestamp
    tarAvg: float  # average across tariff
    zones: list[float]  # measurements for each zone
    est: bool  # was the value estimated using simulation?
    cplt: bool  # literally have no idea what this is


class EnergyConsumptionPerZone(typing.NamedTuple):
    """
        Basically, this is a named tuple that represents the measurements for each zone.

        By zone, it is meant that the tariff can be composed of different timespans, for which the energy consumption is measured and billed separately.
    """
    round_the_clock: float
    daily: float
    nightly: float


class Measurement(typing.NamedTuple):
    """
        This is a named tuple that represents the measurements for a given timestamp.
    """
    timestamp: str
    consumption: EnergyConsumptionPerZone


def date_to_epoch(date: str) -> int:
    return int(
        datetime.datetime.strptime(date, '%d-%m-%Y').timestamp() * 1000
    )


@MEASUREMENTS_ROUTER.get('/energy/info')
async def get_measurements_api_info(request: fastapi.Request) -> fastapi.responses.Response:
    assets_path: str = request.app.extra.get(
        agent.utils.consts.AGENT_CONFIG_FIELD
    ).assets_path
    return fastapi.responses.HTMLResponse(
        content=open(f'{assets_path}/energy_info.html', encoding='utf-8').read(),
    )


@MEASUREMENTS_ROUTER.get('/energy/query')
async def query_measurements(request: fastapi.Request) -> fastapi.responses.Response:
    starting_date = request.query_params.get('date')
    if starting_date is None:
        return fastapi.responses.JSONResponse(
            content={'status': 'error', 'message': 'Missing date parameter'},
            status_code=400
        )
    period = request.query_params.get('period', '').upper()
    if not period:
        return fastapi.responses.JSONResponse(
            content={'status': 'error', 'message': 'Missing period parameter'},
            status_code=400
        )

    current_agent_app_state: fastapi.FastAPI = request.app
    meter_id = current_agent_app_state.extra.get(
        agent.utils.consts.AGENT_METER_ID_FIELD
    )

    authorized_energa_session: requests.Session = current_agent_app_state.extra.get(
        agent.utils.consts.AGENT_ENERGA_SESSION_FIELD
    )  # type: ignore

    with agent.utils.retry.retry_procedure(
        max_retries=current_agent_app_state.extra.get(
            agent.utils.consts.AGENT_CONFIG_FIELD,
        ).max_retries  # type: ignore
    ):
        data_query_url = f'{agent.utils.consts.PPE_DATA_CHARTS_BASE_URL}?mainChartDate={date_to_epoch(starting_date)}&type={period}&meterPoint={meter_id}&mo=A%2B'
        response = authorized_energa_session.get(
            url=data_query_url,
            timeout=current_agent_app_state.extra.get(
                agent.utils.consts.AGENT_CONFIG_FIELD
            ).timeout  # type: ignore
        )
        response.raise_for_status()
    if response.status_code != 200:
        return fastapi.responses.JSONResponse(
            content={'status': 'error', 'message': 'Failed to fetch data'},
            status_code=500
        )

    fetched_data: list[EnergaMeasurementData] = response.json().get('response', {}).get('mainChart', [])
    if not fetched_data:
        return fastapi.responses.JSONResponse(
            content={'status': 'error', 'message': 'No data available'},
            status_code=404
        )

    limit = request.query_params.get('limit', len(fetched_data))
    cost = request.query_params.get('cost', 1.0)

    return fastapi.responses.JSONResponse(
        content={'status': 'success', 'data': _extract_measurement_values_from_fetched_data(
            fetched_data[:int(limit)],
            float(cost)
        )},
        status_code=200
    )


def _extract_measurement_values_from_fetched_data(
    fetched_data: list[EnergaMeasurementData],
    conversion_coefficient: float
) -> list[Measurement]:
    def __energa_data_reducer(
        measurements_collection: list[Measurement],
        measurement_data: EnergaMeasurementData
    ) -> list[Measurement]:
        if 'zones' not in measurement_data or 'tm' not in measurement_data:
            return measurements_collection
        data_for_each_zone = measurement_data.get('zones', (0.0, 0.0, 0.0))
        measurement_time = datetime.datetime.fromtimestamp(
            int(measurement_data.get('tm')) / 1000  # type: ignore
        ).strftime('%Y-%m-%d %H:%M:%S')
        return measurements_collection + [Measurement(measurement_time, EnergyConsumptionPerZone(
            round_the_clock=data_for_each_zone[0] or 0.0 * conversion_coefficient,
            daily=data_for_each_zone[1] or 0.0 * conversion_coefficient,
            nightly=data_for_each_zone[2] or 0.0 * conversion_coefficient
        ))]

    extracted_values: list[Measurement] = functools.reduce(
        __energa_data_reducer,
        fetched_data,
        []
    )
    return [*filter(bool, extracted_values)]
