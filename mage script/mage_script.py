# -*- coding: utf-8 -*-
"""Mage script

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tCSMOwUYTCLJ01F7BNT6vpZNrY4phsvK

## **Data loader** - Loading input data
"""

import io
import pandas as pd
import requests
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    url = 'https://storage.googleapis.com/myfirstproject_uber/uber_data.csv'
    response = requests.get(url)

    return pd.read_csv(io.StringIO(response.text), sep=',')


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'

"""## **Transformer** - Transforming input data"""

import pandas as pd
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your transformation logic here
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
    df = df.drop_duplicates().reset_index(drop=True)
    df['trip_id'] = df.index
    datetime_dm = df[['tpep_pickup_datetime','tpep_dropoff_datetime']].reset_index(drop=True)
    datetime_dm['pickup_hour'] = datetime_dm['tpep_pickup_datetime'].dt.hour
    datetime_dm['pickup_day'] = datetime_dm['tpep_pickup_datetime'].dt.day
    datetime_dm['pickup_year'] = datetime_dm['tpep_pickup_datetime'].dt.year
    datetime_dm['pickup_month'] = datetime_dm['tpep_pickup_datetime'].dt.month
    datetime_dm['dropoff_hour'] = datetime_dm['tpep_dropoff_datetime'].dt.hour
    datetime_dm['dropoff_day'] = datetime_dm['tpep_dropoff_datetime'].dt.day
    datetime_dm['dropoff_year'] = datetime_dm['tpep_dropoff_datetime'].dt.year
    datetime_dm['dropoff_month'] = datetime_dm['tpep_dropoff_datetime'].dt.month
    datetime_dm['datetime_ID'] = datetime_dm.index

    pickup_dm = df[['pickup_longitude','pickup_latitude']].reset_index(drop=True)
    pickup_dm['pickup_ID'] = pickup_dm.index

    dropoff_dm = df[['dropoff_longitude','dropoff_latitude']].reset_index(drop=True)
    dropoff_dm['dropoff_ID'] = dropoff_dm.index

    trip_distance_dm = df[['trip_distance']].reset_index(drop=True)
    trip_distance_dm['trip_distance_ID'] = trip_distance_dm.index

    ratecode_id_type =  {
    1:"Standard rate",
    2:"JFK",
    3:"Newark",
    4:"Nassau or Westchester",
    5:"Negotiated fare",
    6:"Group ride"
    }
    ratecode_dm = df[['RatecodeID']].reset_index(drop=True)
    ratecode_dm['Ratecode_id'] = ratecode_dm.index
    ratecode_dm['Ratecode_name'] = ratecode_dm['RatecodeID'].map(ratecode_id_type)

    payment_id_type = {
    1:"Credit card",
    2:"Cash",
    3:"No charge",
    4:"Dispute",
    5:"Unknown",
    6:"Voided trip"
    }
    payment_dm = df[['payment_type']].reset_index(drop=True)
    payment_dm['payment_ID'] = payment_dm.index
    payment_dm['payment_name'] = payment_dm['payment_type'].map(payment_id_type)

    datetime_dm = datetime_dm[['datetime_ID','tpep_pickup_datetime','pickup_hour','pickup_day', 'pickup_month','pickup_year', 'tpep_dropoff_datetime','dropoff_hour',
       'dropoff_day','dropoff_month', 'dropoff_year' ]]

    pickup_dm = pickup_dm[['pickup_ID','pickup_longitude','pickup_latitude']]

    dropoff_dm = dropoff_dm[['dropoff_ID','dropoff_longitude','dropoff_latitude']]

    ratecode_dm = ratecode_dm[['Ratecode_id','RatecodeID','Ratecode_name']]

    payment_dm = payment_dm[['payment_ID','payment_type','payment_name']]

    trip_distance_dm = trip_distance_dm[['trip_distance_ID','trip_distance']]

    fact_table = df[['VendorID','passenger_count','store_and_fwd_flag','fare_amount','extra', 'mta_tax', 'tip_amount', 'tolls_amount','improvement_surcharge', 'total_amount', 'trip_id']].merge(datetime_dm, left_on = 'trip_id',right_on = 'datetime_ID').merge(payment_dm,left_on = 'trip_id',right_on = 'payment_ID').merge(trip_distance_dm,left_on = 'trip_id',right_on = 'trip_distance_ID').merge(ratecode_dm,left_on = 'trip_id',right_on = 'Ratecode_id').merge(dropoff_dm,left_on = 'trip_id',right_on = 'dropoff_ID').merge(pickup_dm,left_on = 'trip_id',right_on = 'pickup_ID')

    fact_table = fact_table[['VendorID','pickup_ID','dropoff_ID','datetime_ID','payment_ID','Ratecode_id','trip_distance_ID','passenger_count','trip_distance','fare_amount','mta_tax','tip_amount','tolls_amount','improvement_surcharge','total_amount']]
    # print(fact_table.head())


    return {"datetime_dm":datetime_dm.to_dict(orient="dict"),
    "pickup_dm":pickup_dm.to_dict(orient="dict"),
    "dropoff_dm":dropoff_dm.to_dict(orient="dict"),
    "ratecode_dm":ratecode_dm.to_dict(orient="dict"),
    "payment_dm":payment_dm.to_dict(orient="dict"),
    "trip_distance_dm":trip_distance_dm.to_dict(orient="dict"),
    "fact_table":fact_table.to_dict(orient="dict")}


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'

"""## **Data Exporter** - Big Query"""

from mage_ai.settings.repo import get_repo_path
from mage_ai.io.bigquery import BigQuery
from mage_ai.io.config import ConfigFileLoader
from pandas import DataFrame
from os import path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_big_query(data, **kwargs) -> None:
    """
    Template for exporting data to a BigQuery warehouse.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#bigquery
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'

    for key,value in data.items():

        table_id = 'fit-visitor-393013.data_engineering_p1.{}'.format(key)
        BigQuery.with_config(ConfigFileLoader(config_path, config_profile)).export(
            DataFrame(value),
            table_id,
            if_exists='replace',  # Specify resolution policy if table name already exists
        )