from vinyl.lib.project import Project
from vinyl.lib.table import VinylTable


class QueryEngineResult:
    def __init__(self, table: VinylTable):
        self.table = table

    def to_pandas(self):
        return self.table.execute("pandas")

    def to_records(self):
        df = self.to_pandas()
        for col, dtype in df.dtypes.items():
            if dtype.kind == "M":  # Check for datetime64 types
                df[col] = df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")

        return df.to_dict("records")

    def columns(self):
        return self.table.columns

    def numpy_rows(self):
        df = self.to_pandas()
        return [tuple(row) for row in df.to_numpy()]


class QueryEngine:
    def __init__(self, project: Project):
        self.project = project

    def _model(self, name: str, limit: int):
        table = self.project._get_model(name)
        return QueryEngineResult(table.limit(limit))

    def _metric(
        self,
        store: str,
        grain: str,
        metrics: list[str] | None = None,
        dimensions: list[str] | None = None,
        limit: int | None = 1000,
    ):
        if "=" not in grain:
            raise ValueError("Invalid bucket format. Ex: 'days=1'")

        bucket_grain, bucket_value = grain.split("=")
        met_store = self.project._get_metric_store(store)
        combined_keys = [k for k in met_store._metrics_dict] + [
            k for k in met_store._derived_metrics
        ]

        cols = [
            getattr(met_store, name)
            for name in combined_keys
            if metrics is None or name in metrics
        ]

        if dimensions is None:
            dimensions = []
        else:
            dimensions = [getattr(met_store, name) for name in dimensions]

        table = met_store.select(
            [
                met_store.ts.dt.floor(**{bucket_grain: int(bucket_value)}),
                *dimensions,
                *cols,
            ]
        )

        if limit is None:
            return QueryEngineResult(table)

        else:
            return QueryEngineResult(table.limit(limit))
