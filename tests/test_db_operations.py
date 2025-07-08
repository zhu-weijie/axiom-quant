from unittest.mock import MagicMock, patch

import pandas as pd

from axiomquant.database.operations import write_dataframe_to_db


@patch("axiomquant.database.operations.get_db_engine")
def test_write_dataframe_to_db(mock_get_engine):
    mock_engine = MagicMock()
    mock_get_engine.return_value = mock_engine

    sample_df = pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})

    sample_df.to_sql = MagicMock()

    write_dataframe_to_db(sample_df, "test_table")

    mock_get_engine.assert_called_once()

    sample_df.to_sql.assert_called_once_with(
        "test_table", mock_engine, if_exists="append", index=False
    )


@patch("axiomquant.database.operations.get_db_engine")
def test_write_dataframe_to_db_empty_df(mock_get_engine):
    empty_df = pd.DataFrame()
    empty_df.to_sql = MagicMock()

    write_dataframe_to_db(empty_df, "test_table")

    mock_get_engine.assert_not_called()
    empty_df.to_sql.assert_not_called()
