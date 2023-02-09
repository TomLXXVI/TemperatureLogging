from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px


class MeasurementFileReader:
    csv_settings = {
        'sep': ';',
        'decimal': ','
    }

    def __init__(self, data_folder_path: str):
        """
        Create instance of `MeasurementReader` class.

        Parameters
        ----------
        data_folder_path:
            Path to the folder where csv measurement files are stored.
        """
        self.data_folder_path = Path(data_folder_path)
        self.measurement_data: pd.DataFrame | None = None
        self.locations: list[str] | None = None

    def read(self, file_name: str | Path, location: str | None = None) -> pd.DataFrame:
        """
        Read the specified csv measurement file.

        Parameters
        ----------
        file_name:
            The name of the measurement file without csv extension added.
        location: optional
            The name of the location where the measurements were taken. If None,
            `file_name` is used to specify the measurement location.

        Returns
        -------
        Pandas DataFrame object. The index of the dataframe is the date and time
        when measurements were recorded. The location is added to the dataframe
        in a separate column.
        """
        file_path = self.data_folder_path / f'{file_name}.csv'
        self.measurement_data = pd.read_csv(
            filepath_or_buffer=file_path,
            sep=self.csv_settings['sep'],
            decimal=self.csv_settings['decimal'],
            usecols=[1, 2, 3],
            parse_dates=[0],
            infer_datetime_format=True,
            dayfirst=True
        )
        self.measurement_data = self.measurement_data.set_index(self.measurement_data.columns[0])
        if location:
            self.measurement_data['location'] = [location] * self.measurement_data.shape[0]
        else:
            self.measurement_data['location'] = [file_name] * self.measurement_data.shape[0]
        return self.measurement_data

    def batch_read(
        self,
        file_names: list[str] | None = None,
        locations: list[str] | None = None
    ) -> pd.DataFrame:
        """
        Read multiple measurement files into one Pandas Dataframe object.

        Parameters
        ----------
        file_names: optional
            List of names of measurement files. If None, all csv files in
            `self.data_folder_path` will be included.
        locations: optional
            List of locations where measurements where taken, in the same order
            as the list of filenames. If None, the file names will be used to
            specify the measurement locations.

        Returns
        -------
        Pandas DataFrame object. The index of the dataframe is the date and time
        when measurements were recorded.
        """
        if file_names is None:
            file_names = [f.stem for f in self.data_folder_path.glob('*.csv')]
            # note: `stem` removes the file extension from the filename (actually
            # a Path object)
        if locations:
            df_lst = [self.read(fn, loc) for fn, loc in zip(file_names, locations)]
            self.locations = locations
        else:
            df_lst = [self.read(fn, None) for fn in file_names]
            self.locations = [str(fn) for fn in file_names]
        self.measurement_data = pd.concat(df_lst).sort_index()
        return self.measurement_data

    def get_datetime_limits(self) -> tuple[datetime, datetime]:
        start = self.measurement_data.index[0]
        end = self.measurement_data.index[-1]
        return start, end

    def get_measurements(
        self,
        start: datetime,
        end: datetime,
        locations: list[str] | None = None
    ) -> pd.DataFrame:
        """
        Get measurements between start and end at the specified locations.

        Parameters
        ----------
        start:
            First date and time of the measurement range.
        end:
            Last date and time of the measurement range.
        locations: optional
            The locations from which measurements are wanted. If None,
            measurements from all locations will be returned.

        Returns
        -------
        Pandas DataFrame object.
        """
        df = self.measurement_data
        if start and end:
            df = self.measurement_data.loc[start:end]
        if locations:
            df = df[df.location.isin(locations)]
        return df


def plot_chart(
    measurement_data: pd.DataFrame,
    y_index: int,
    color_index: int,
    **kwargs
):
    chart = px.line(
        data_frame=measurement_data,
        y=measurement_data.columns[y_index],
        color=measurement_data.columns[color_index],
        width=kwargs.get('width', 800),
        height=kwargs.get('height', 600)
    )
    return chart


if __name__ == '__main__':
    
    data_folder_path = '../data'
    mr = MeasurementFileReader(data_folder_path)
    df = mr.batch_read()
    print(df)
    start, end = mr.get_datetime_limits()
    print(start, end)
    df = mr.get_measurements(datetime(2023, 2, 3), datetime(2023, 2, 5), locations=['inkomhal'])
    print(df)
    chart = plot_chart(df, 0, 2)
    chart.show()
