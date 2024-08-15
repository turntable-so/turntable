from __future__ import annotations

import copy
import warnings
from collections.abc import Iterable
from typing import Any, Callable, Sequence, Set

import ibis
import ibis.expr.datatypes as dt
import ibis.expr.types as ir
import ibis.selectors as s
from ibis import _

from vinyl.lib.column import VinylColumn, _demote_args
from vinyl.lib.column_methods import (
    ColumnBuilder,
    ColumnListBuilder,
    _process_cols_arg,
    column_type,
)
from vinyl.lib.constants import (
    _DIMENSION_LABEL,
    _METRIC_LABEL,
    _SCHEMA_LABEL,
    _TS_COL_NAME,
)
from vinyl.lib.enums import FillOptions, WindowType
from vinyl.lib.table import VinylTable
from vinyl.lib.table_methods import _adjust_fill_list, _join_with_removal
from vinyl.lib.temporal import _set_timezone
from vinyl.lib.utils.functions import _validate
from vinyl.lib.utils.text import _split_interval_string


class Metric:
    _tbl: VinylTable
    _name: str  # allows pydantic to still work
    _ts: Callable[..., Any]
    _agg: Callable[..., Any]
    _by: column_type
    _fill: FillOptions | Callable[..., Any]

    def __init__(
        self,
        tbl: VinylTable,
        agg: Callable[..., Any],
        ts: Callable[..., Any],
        by: column_type,
        fill=FillOptions.null,
    ):
        self._tbl = tbl
        self._agg = agg
        self._ts = ts
        self._by = by
        self._fill = fill

        # set name
        name = ColumnBuilder(self._tbl.tbl, self._agg, passthrough_deferred=True)._name
        if name is None or not isinstance(name, str):
            raise ValueError("Metric name must be a valid string")
        else:
            self._name = name

        # ensure ts is a timestamp
        self._ts = _set_timezone(self._tbl.tbl, self._ts)

        # ensure ts name is set to TS_COL_NAME constant
        ts_orig = copy.deepcopy(self._ts)
        self._ts = lambda t: ts_orig(t).name(_TS_COL_NAME)

    @property
    def _dimension_names(self) -> Set[str]:
        if self._by is None:
            return set()
        vinyl_by = ColumnListBuilder(self._tbl.tbl, self._by, passthrough_deferred=True)
        return set([n for n in vinyl_by._names if n is not None])

    def _to_dict(self) -> dict[str, Any]:
        return {
            "tbl": self._tbl,
            "name": self._name,
            "agg": self._agg,
            "ts": self._ts,
            "by": self._by,
            "fill": self._fill,
        }


def _get_dimension_names(metrics: Sequence[Metric]) -> Set[str]:
    return set().union(*[m._dimension_names for m in metrics])


class MetricStore:
    _all_metrics_dict: dict[str, Metric] = dict()
    _all_dimension_names: set[str] = set()

    _mutable: bool
    _default_tbl: VinylTable | None
    _trailing_intervals: list[ibis.interval] | None
    _metrics_dict: dict[str, Metric]
    _dimension_names: set[str]
    _derived_metrics: dict[str, ir.Deferred]

    # key will always be a vinylTable, but can't use it here due to a circular reference
    _tbl_dict: dict[VinylTable, dict[str, Any]] = {}

    __dict__: dict[str, Any]

    def __init__(
        self,
        metrics: Sequence[Metric] = [],
        derived_metrics: dict[str, ir.Deferred] = {},
        default_tbl: VinylTable | None = None,
    ):
        self._mutable = False
        self._default_tbl = default_tbl
        self._trailing_intervals = None
        self._metrics_dict = {m._name: m for m in metrics}
        self._derived_metrics = derived_metrics
        self._dimension_names = _get_dimension_names(metrics)

        self._tbl_dict = {}
        for m in metrics:
            if m._tbl not in self._tbl_dict:
                self._tbl_dict[m._tbl] = {}
                self._tbl_dict[m._tbl][_METRIC_LABEL] = set()
                self._tbl_dict[m._tbl][_DIMENSION_LABEL] = set()
                self._tbl_dict[m._tbl][_SCHEMA_LABEL] = {}

            self._tbl_dict[m._tbl][_METRIC_LABEL].add(m._name)
            self._tbl_dict[m._tbl][_DIMENSION_LABEL].update(m._dimension_names)
            col_helper_it = ColumnBuilder(m._tbl.tbl, m._agg, passthrough_deferred=True)
            self._tbl_dict[m._tbl][_SCHEMA_LABEL].setdefault(
                col_helper_it._name, col_helper_it._type
            )
            self._tbl_dict[m._tbl][_SCHEMA_LABEL][_TS_COL_NAME] = dt.Timestamp()
            if m._by is not None and isinstance(m._by, Iterable):
                for dim in ColumnListBuilder(
                    m._tbl.tbl, m._by, passthrough_deferred=True
                ):
                    self._tbl_dict[m._tbl][_SCHEMA_LABEL].setdefault(
                        dim._name, dim._type
                    )

        MetricStore._address_naming_conflicts(self._metrics_dict)
        MetricStore._append(self._metrics_dict)

        self._set_columns()

    # create column function autocomplete
    def __getattr__(self, name) -> VinylColumn:
        return self.__getattribute__(name)

    def _copy(self) -> MetricStore:
        return MetricStore(
            list(self._metrics_dict.values()), self._derived_metrics, self._default_tbl
        )

    def _set_columns(self):
        # set columns
        count = 0
        for name in ["ts", *self._dimension_names, *self._metrics_dict]:
            col = VinylColumn(getattr(_, name))
            setattr(self, name, col)
            setattr(self, f"_{count}", col)
            count += 1

        for k, v in self._derived_metrics.items():
            setattr(self, k, v)
            setattr(self, f"_{count}", v)
            count += 1

    def _clear_columns(self):
        for name in self.__dict__.copy():
            if name not in [
                "_mutable",
                "_default_tbl",
                "_trailing_intervals",
                "_metrics_dict",
                "_dimension_names",
                "_tbl_dict",
                "_derived_metrics",
            ]:
                delattr(self, name)

    def _reset_columns(self):
        self._clear_columns()
        self._set_columns()

    def __add__(self, other: MetricStore) -> MetricStore:
        if not isinstance(other, MetricStore):
            raise ValueError(
                f"Can only add two MetricStores together, not a {type(other)}"
            )
        if self._default_tbl is None:
            return other
        if other._default_tbl is None:
            return self

        if self._default_tbl != other._default_tbl:
            raise ValueError(
                "Can't add two MetricStores with different default tables. Use a join (e.g. tbl1 * tbl2) instead."
            )
        combined_metrics = list(self._metrics_dict.values()) + list(
            other._metrics_dict.values()
        )
        combined_derived_metrics = {**self._derived_metrics, **other._derived_metrics}

        out = MetricStore(
            combined_metrics,
            combined_derived_metrics,
            self._default_tbl,
        )
        out._reset_columns()
        if self._mutable:
            self.__dict__ = out.__dict__
            self.__dict__["_mutable"] = True  # reset mutability to True
        return out

    def __radd__(self, other: MetricStore) -> MetricStore:
        if not isinstance(other, MetricStore):
            raise ValueError(
                f"Can only add two MetricStores together, not a {type(other)}"
            )
        return other.__add__(self)

    # Make callable so that @model wrapper works
    def __call__(self):
        return self

    # Make mutable when using in a context manager
    def __enter__(self):
        # Create a copy of the original object and make the object mutable
        new = MetricStore(list(self._metrics_dict.values()), self._default_tbl)
        new._mutable = True
        return new

    def __exit__(self, exc_type, exc_value, traceback):
        # Exit logic here
        pass

    def select(
        self,
        cols: column_type,
        trailing: list[int | None] = [None],
    ) -> VinylTable:
        """
        Retrieves the selected columns from the MetricStore.

        For `cols`, you may select metrics, dimensions, or the timestamp column. You can also select any expressions (e.g. met1 + met2) based on metrics or dimensions, but not a mix of metrics and dimensions in the same expression. If you select the timestamp column, you must use the `.floor` method to bucket the timestamps to a desired interval.

        If no trailing intervals are provided, the function will return the aggregated value for each col. If you provide trailing intervals, the function will return the aggregated value over the trailing intervals. For example, if you provide [1, 2], the function will return the aggregated value **for each `col`** over the interval and the previous interval, and the aggregated value over the interval and the previous two intervals.
        """
        if self._default_tbl is None:
            raise ValueError("Can't select from an empty MetricStore.")
        cols_adj = _process_cols_arg(
            self._default_tbl.tbl, cols, passthrough_deferred=True
        )
        return MetricSelect(self, cols=cols_adj, intervals=trailing)._select()

    def metric(
        self,
        cols: (
            ir.Scalar
            | Callable[..., ir.Scalar]
            | list[ir.Scalar | Callable[..., ir.Scalar]]
            | dict[str, ir.Scalar | Callable[..., ir.Scalar]]
        ),
        ts: ir.TimestampValue | Callable[..., ir.TimestampValue],
        by: (
            ir.Value
            | Callable[..., ir.Value]
            | Sequence[ir.Value | Callable[..., ir.Value]]
        ) = [],
        fill: (
            FillOptions | Callable[..., Any]
        ) = FillOptions.null,  # all metrics have fill
        tbl: VinylTable | None = None,
    ):
        if tbl is None:
            if self._default_tbl is None:
                raise ValueError(
                    "No default table set. Please provide a table to the metric function."
                )
            tbl = self._default_tbl
        vinyl_cols = ColumnListBuilder(tbl.tbl, cols, passthrough_deferred=True)
        if len(vinyl_cols._cols) == 0:
            raise ValueError("Must provide at least one metric to metric function")

        vinyl_by = ColumnListBuilder(tbl.tbl, by, passthrough_deferred=True)
        vinyl_ts = ColumnBuilder(tbl.tbl, ts, passthrough_deferred=True)

        fill_list = _adjust_fill_list(len(vinyl_cols._cols), fill)

        mets = []
        for i, v in enumerate(vinyl_cols):
            met = Metric(
                tbl=tbl,
                agg=v._lambdaized,
                ts=vinyl_ts._lambdaized,
                by=vinyl_by._lambdaized,
                fill=fill_list[i],
            )
            mets.append(met)
        out = MetricStore(metrics=mets, derived_metrics={}, default_tbl=tbl)
        combined = self + out
        return combined

    def derive(
        self,
        metrics: (
            ir.Scalar
            | Callable[..., ir.Scalar]
            | list[ir.Scalar | Callable[..., ir.Scalar]]
            | dict[str, ir.Scalar | Callable[..., ir.Scalar]]
        ),
    ):
        """
        Add a derived metric to the MetricStore. Derived metrics are calculated from existing metrics in the MetricStore.

        Please do not include any other columns in the derived metric. This could cause unexpected behavior.
        """
        # build mock tbl to help with getting column names
        mock_cols = []
        for name, met in self._metrics_dict.items():
            type_ = ColumnBuilder(met._tbl.tbl, met._agg)._type
            mock_cols.append((name, type_))
        mock_tbl = ibis.table(ibis.schema(mock_cols))
        x = ColumnListBuilder(mock_tbl, metrics, passthrough_deferred=True)

        # build derived metrics dict
        new_derived_metrics = {
            col._name: col._col
            for col in x._cols
            if col._name is not None and col._col is not None
        }
        for k in new_derived_metrics:
            if k in self._metrics_dict:
                raise ValueError(
                    f"Derived metric name {k} already exists in the global metric store. Please rename the derived metric."
                )

        # union with self
        out = self + MetricStore(
            derived_metrics=new_derived_metrics, default_tbl=self._default_tbl
        )
        return out

    def _trailing(self, intervals: list[int | None] = [None]):
        if isinstance(intervals[0], str):
            intervals = [_split_interval_string(i) for i in intervals]

        ## arguments here should be like (1, "d")
        self._trailing_invervals = [ibis.interval(*i) for i in intervals]

    @classmethod
    def _append(cls, new_metrics_dict):
        cls._all_metrics_dict.update(new_metrics_dict)
        cls._all_dimension_names = cls._all_dimension_names | _get_dimension_names(
            new_metrics_dict.values()
        )

    @classmethod
    def _address_naming_conflicts(cls, new_metrics_dict: dict[str, Metric]):
        # set warnings for metric name conflicts
        all_intersections = set(new_metrics_dict.keys()) & set(
            cls._all_metrics_dict.keys()
        )
        nontrivial_intersections = set()
        for i in all_intersections:
            new_metrics_entry = new_metrics_dict[i]
            cls_metrics_entry = cls._all_metrics_dict[i]
            if hash(new_metrics_entry._agg(new_metrics_entry._tbl.tbl)) != hash(
                cls_metrics_entry._agg(cls_metrics_entry._tbl.tbl)
            ):
                nontrivial_intersections.add(i)

        if any(nontrivial_intersections):
            warning_txt = f"\n\nMetric(s) {nontrivial_intersections} already exist in the global metric store. The new metric(s) will overwrite the old metric(s).\n\n Here's how the formulas will change:\n"
            for k, v in new_metrics_dict.items():
                if k in nontrivial_intersections:
                    warning_txt += f"- {k}: {cls._all_metrics_dict[k]._agg(cls._all_metrics_dict[k]._tbl.tbl)} -> {v._agg(v._tbl.tbl)}\n"
            # TODO: these are showing up in tests, need to find a way to warn otherwise
            # warnings.warn(message=warning_txt)

        # raise error when metric name conflicts with dimension name
        new_all_metric_names = set(new_metrics_dict.keys()) | set(
            cls._all_metrics_dict.keys()
        )
        new_all_dimension_names = _get_dimension_names(
            [v for v in new_metrics_dict.values()]
        ) | set(cls._all_dimension_names)

        if any(new_all_metric_names & new_all_dimension_names):
            raise ValueError(
                f"\n\nMetric name(s) {new_all_metric_names} conflict with dimension name(s) {new_all_dimension_names}. Please rename the metric(s) or dimension(s)."
            )


class MetricSelect:
    _metric_store: MetricStore
    _intervals: list[int | None]
    _ts: list[ir.Value]
    _dimensions: list[ir.Value]
    _temp_dimensions: list[ir.Value]
    _temp_metrics: list[ir.Value]
    _tbl_ts_metrics_to_select: dict[VinylTable, list[ir.Value]]

    _raw_metric_tbls: list[VinylTable]
    _all_exprs: list[ir.Value]
    _combined_schema: VinylTable

    def __init__(
        self,
        MetricStore: MetricStore,
        cols: list[ir.Value],
        intervals: list[int | None] = [None],
    ):
        self._metric_store = MetricStore
        self._intervals = intervals
        self._ts = []
        self._dimensions = []
        self._temp_dimensions = []
        self._temp_metrics = []

        # helper to select metrics from the same tbl together as long as they have the same ts
        self._tbl_ts_metrics_to_select = {}

        # helper to store raw metric tables
        self._raw_metric_tbls = []

        self._all_exprs = cols

        # create combined schema
        for i, vals in enumerate(list(self._metric_store._tbl_dict.values())):
            if i == 0:
                self._combined_schema = VinylTable._create_from_schema(
                    vals[_SCHEMA_LABEL]
                )
            else:
                self._combined_schema += VinylTable._create_from_schema(
                    vals[_SCHEMA_LABEL]
                )

    def _process_unaltered_col(self, col, col_name):
        vinyl_col = ColumnBuilder(
            self._combined_schema.tbl, col, passthrough_deferred=True
        )
        if col_name in self._metric_store._dimension_names:
            self._dimensions.append(vinyl_col._lambdaized)
        elif col_name in self._metric_store._metrics_dict:
            met = self._metric_store._metrics_dict[col_name]
            key_it = met._tbl.define(met._ts(met._tbl))  # use ts column as unique
            self._tbl_ts_metrics_to_select.setdefault(key_it, set())
            self._tbl_ts_metrics_to_select[key_it].add(col_name)
        elif col_name == _TS_COL_NAME:
            raise ValueError(
                "Can't select the raw ts column. Consider using the .truncate() or .bucket() method"
            )
        else:
            raise ValueError(f"{col_name} is not a valid column name")

    def _process_derived_col(self, col, col_name):
        vinyl_col = ColumnBuilder(
            self._combined_schema.tbl, col, passthrough_deferred=True
        )
        sources = vinyl_col._sources
        source_types = []
        for source in sources:
            if source in self._metric_store._dimension_names:
                source_types.append(_DIMENSION_LABEL)
            elif source in self._metric_store._metrics_dict:
                source_types.append(_METRIC_LABEL)
            elif source == _TS_COL_NAME:
                source_types.append(_TS_COL_NAME)
            else:
                raise ValueError(f"{source} is not a valid column name")

            if len(set(source_types)) > 1:
                raise ValueError(
                    "Can't mix metrics and dimensions in the same expression"
                )
            elif source_types[0] == _TS_COL_NAME:
                self._ts.append(vinyl_col._lambdaized)
            elif source_types[0] == _DIMENSION_LABEL:
                self._temp_dimensions.append(vinyl_col._lambdaized)
                # ensure that sources are added to dimensions so derivation works later
                self._dimensions.append(source)
            elif source_types[0] == _METRIC_LABEL:
                self._temp_metrics.append(vinyl_col._lambdaized)
                # ensure that sources are added to metrics so derivation works later
                met_source = self._metric_store._metrics_dict[source]
                key_it = met_source._tbl.define(
                    met_source._ts(met_source._tbl)
                )  # use ts column as unique so that the same tables with different ts columns are aggregated separately
                self._tbl_ts_metrics_to_select.setdefault(key_it, set())
                self._tbl_ts_metrics_to_select[key_it].add(source)
            else:
                raise ValueError(f"{col_name} is not a valid column name")

    def _process_col(self, col):
        vinyl_col = ColumnBuilder(
            self._combined_schema.tbl, col, passthrough_deferred=True
        )
        col_name = vinyl_col._name
        mets_to_select = []
        for i in self._tbl_ts_metrics_to_select.values():
            mets_to_select.extend(list(i))
        cur_col_names_helper = [
            d
            for d in list(self._dimensions)
            + list(self._temp_dimensions)
            + list(self._temp_metrics)
            + mets_to_select
        ]
        cur_col_names = ColumnListBuilder(
            self._combined_schema.tbl, cur_col_names_helper, passthrough_deferred=True
        )._names

        # skip if column is already in dimensions or metrics already selected (including derived)
        if col_name in cur_col_names:
            return

        if vinyl_col._is_unaltered:
            self._process_unaltered_col(vinyl_col._lambdaized, col_name)

        else:
            self._process_derived_col(vinyl_col._lambdaized, col_name)

    def _build_final_tbls(self):
        for interval in self._intervals:
            raw_metric_tbl_interval = []
            mets_rename_dict = {}
            # prepare raw metric tables
            for tbl, met_names in self._tbl_ts_metrics_to_select.items():
                tbl = tbl._copy()  # copy tbl to ensure no mutability issues
                mets_it = [
                    self._metric_store._metrics_dict[name]._agg for name in met_names
                ]
                fill_it = [
                    self._metric_store._metrics_dict[name]._fill for name in met_names
                ]
                vinyl_cols = ColumnListBuilder(
                    tbl.tbl, mets_it, passthrough_deferred=True
                )
                source_cols = vinyl_cols._sources_as_deferred_resolved(tbl.tbl)
                vinyl_dims = ColumnListBuilder(
                    tbl.tbl, self._dimensions, passthrough_deferred=True
                )
                source_dims = vinyl_dims._names_as_deferred
                vinyl_ts = ColumnListBuilder(
                    tbl.tbl, self._ts, passthrough_deferred=True
                )
                source_ts = vinyl_ts._names
                ts_original_source = vinyl_ts._get_direct_col_sources(unique=True)

                if interval is None:
                    tbl = tbl.select(
                        source_cols,
                        by=[col(tbl.tbl) for col in self._dimensions],
                        sort=[col(tbl.tbl) for col in self._ts],
                    )

                    out_it = tbl.aggregate(
                        cols=[met(tbl.tbl) for met in mets_it],
                        by=source_dims,
                        sort=source_ts,
                        fill=fill_it,
                    )
                else:
                    tbl = tbl.aggregate_all(
                        col_selector=source_cols,
                        f=lambda x: x.collect(),
                        by=[col(tbl.tbl) for col in self._dimensions],
                        sort=[col(tbl.tbl) for col in self._ts],
                        fill=FillOptions.null,  # trailing metrics only support null fill,
                    )
                    collected_tbl_with_trailing = tbl.select_all(
                        col_selector=vinyl_cols._sources_as_deferred_resolved(tbl.tbl),
                        f=lambda x: x.collect().array.flatten(),
                        by=[dim.resolve(tbl.tbl) for dim in source_dims],
                        sort=vinyl_ts._names_as_deferred_resolved(tbl.tbl),
                        window_type=WindowType.rows,
                        window_bounds=(-interval, 0),
                        rename=False,
                    )

                    ## NOTE: to replace once Vinyl mutate function is written
                    unnested = collected_tbl_with_trailing.define_all(
                        col_selector=[s.of_type(dt.Array)],
                        f=[lambda y: y.array.unnest()],
                        rename=False,
                    ).rename(
                        {v: source_ts[i] for i, v in enumerate(ts_original_source)}
                    )  # rename ts to make sure transformation is available for the fill in next step

                    out_it = unnested.aggregate(
                        cols=[met(unnested.tbl) for met in mets_it],
                        by=[dim.resolve(unnested.tbl) for dim in source_dims],
                        sort=[col(unnested.tbl) for col in self._ts],
                        fill=FillOptions.null,
                    )

                    mets_rename_dict.update()

                raw_metric_tbl_interval.append(out_it)

            # join together
            joined_raw_metric_tbl_interval = raw_metric_tbl_interval[0]
            for tbl in raw_metric_tbl_interval[1:]:
                # Takes connection replace of first table, this will fail if there are two different connections in the list
                joined_raw_metric_tbl_interval = VinylTable(
                    _join_with_removal(
                        joined_raw_metric_tbl_interval.tbl, tbl.tbl
                    )._arg,
                    _conn_replace=joined_raw_metric_tbl_interval._conn_replace,
                    _twin_conn_replace=joined_raw_metric_tbl_interval._twin_conn_replace,
                    _col_replace=joined_raw_metric_tbl_interval._col_replace,
                )

            # calculate derived dimensions and metrics
            for col in self._temp_dimensions + self._temp_metrics:
                joined_raw_metric_tbl_interval = joined_raw_metric_tbl_interval.define(
                    col(joined_raw_metric_tbl_interval.tbl)
                )

            # reorder to match original requested order
            cols_to_select = [
                col.resolve(joined_raw_metric_tbl_interval.tbl)
                for col in ColumnListBuilder(
                    self._combined_schema.tbl,
                    self._all_exprs,
                    passthrough_deferred=True,
                )._names_as_deferred
            ]
            joined_raw_metric_tbl_interval = joined_raw_metric_tbl_interval.select(
                cols_to_select
            )

            # rename trailing metrics
            if interval is not None:
                to_rename = [
                    i.get_name()
                    for i in s.where(
                        lambda x: x.get_name() not in source_ts + vinyl_dims._names
                    ).expand(joined_raw_metric_tbl_interval.tbl)
                ]
                joined_raw_metric_tbl_interval = joined_raw_metric_tbl_interval.rename(
                    {f"{v}_{interval}": v for v in to_rename}
                )
            self._raw_metric_tbls.append(joined_raw_metric_tbl_interval)

    def _select(self):
        for col in self._all_exprs:
            self._process_col(col)

        # build raw metric tables
        self._build_final_tbls()

        # join raw metric tables
        joined_raw_metric_tbl = self._raw_metric_tbls[0]
        for tbl in self._raw_metric_tbls[1:]:
            # Takes connection replace of first table, this will fail if there are two different connections in the list
            joined_raw_metric_tbl = VinylTable(
                _join_with_removal(joined_raw_metric_tbl.tbl, tbl.tbl)._arg,
                _conn_replace=joined_raw_metric_tbl._conn_replace,
                _twin_conn_replace=joined_raw_metric_tbl._twin_conn_replace,
                _col_replace=joined_raw_metric_tbl._col_replace,
            )

        # sort outputs
        final = joined_raw_metric_tbl.sort(s.all())

        return final


# Add pydantic validations. Need to do after function definition to make sure return class (VinylTable) is available to pydantic. Need to demote_args outside of the function to ensure validate works correctly
MetricStore.select = _demote_args(_validate(MetricStore.select))  # type: ignore[method-assign]
MetricStore.metric = _demote_args(_validate(MetricStore.metric))  # type: ignore[method-assign]
