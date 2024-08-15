from enum import Enum
from typing import Any, Callable, Literal

from vinyl.lib.column_methods import (
    ColumnBuilder,
    ColumnListBuilder,
    base_column_type,
    column_type_without_dict,
)
from vinyl.lib.settings import PyProjectSettings


class geom(Enum):
    from lets_plot import (
        aes,
        geom_area,
        geom_area_ridges,
        geom_bar,
        geom_bin2d,
        geom_boxplot,
        geom_density,
        geom_histogram,
        geom_line,
        geom_point,
        geom_smooth,
        geom_violin,
        position_dodge,
        ylab,
    )
    from lets_plot.plot.core import LayerSpec

    scatter: Callable[..., LayerSpec] = geom_point()
    line: Callable[..., LayerSpec] = geom_line()
    bar: Callable[..., LayerSpec] = geom_bar(stat="identity", position=position_dodge())
    area: Callable[..., LayerSpec] = geom_area()
    stacked_bar: Callable[..., LayerSpec] = geom_bar(stat="identity")
    percent_bar: Callable[..., LayerSpec] = (
        geom_bar() + aes(y="..prop..") + ylab("Percent of total")
    )
    histogram: Callable[..., LayerSpec] = geom_histogram()
    histogram_2d: Callable[..., LayerSpec] = geom_bin2d()
    violin: Callable[..., LayerSpec] = geom_violin()
    boxplot: Callable[..., LayerSpec] = geom_boxplot()
    density: Callable[..., LayerSpec] = geom_density()
    ridge: Callable[..., LayerSpec] = geom_area_ridges()
    trendline_lm: Callable[..., LayerSpec] = geom_smooth()
    trendline_loess: Callable[..., LayerSpec] = geom_smooth(method="loess")


class BaseChart:
    _mode: Literal["light", "dark"] = "dark"
    _geoms: geom | list[geom]
    _source: Any  # will be VinylTable, but use Any to avoid recursion
    x: base_column_type
    y: base_column_type | None
    color: base_column_type | None
    fill: base_column_type | None
    size: base_column_type | None
    alpha: base_column_type | None
    facet: column_type_without_dict | None
    _coord_flip: bool = False

    def __init__(
        self,
        geoms: geom | list[geom],
        source: Any,  # will be VinylTable, but use Any to avoid recursion
        x: base_column_type,
        y: base_column_type | None = None,
        color: base_column_type | None = None,
        fill: base_column_type | None = None,
        size: base_column_type | None = None,
        alpha: base_column_type | None = None,
        facet: column_type_without_dict | None = None,
        coord_flip: bool = False,
    ):
        self._geoms = geoms
        self._source = source
        self.x = x
        self.y = y
        self.color = color
        self.fill = fill
        self.size = size
        self.alpha = alpha
        self.facet = facet
        self.coord_flip = coord_flip

    def _show(self):
        from lets_plot import (
            aes,
            coord_flip,
            facet_grid,
            facet_wrap,
            flavor_darcula,
            ggplot,
            scale_x_datetime,
            scale_y_datetime,
        )

        adj_facet = self.facet if isinstance(self.facet, list) else [self.facet]
        all_cols = [
            x
            for x in [self.x]
            + [self.y]
            + [self.color]
            + [self.fill]
            + [self.size]
            + [self.alpha]
            + adj_facet
            if x is not None
        ]

        adj_data = self._source.define(all_cols).execute("pandas")

        ## make sure all cols are in there,
        vinyl_x = ColumnBuilder(self._source.tbl, self.x)
        type_x = vinyl_x._type
        if self.y is not None:
            vinyl_y = ColumnBuilder(self._source.tbl, self.y)
            type_y = vinyl_y._type
        aes_dict = {}
        for var in ["x", "y", "color", "fill", "size"]:
            attr = getattr(self, var)
            if attr is not None:
                aes_dict[var] = ColumnBuilder(self._source.tbl, attr)._name

        plot = ggplot(adj_data, aes(**aes_dict))
        if isinstance(self._geoms, list):
            for g in self._geoms:
                plot += g.value
        elif self._geoms is not None:
            plot += self._geoms.value
        if self.facet is not None:
            facet_names = ColumnListBuilder(self._source.tbl, adj_facet)._names
            if len(adj_facet) > 1:
                plot += facet_grid(
                    facet_names[0],
                    facet_names[1],
                )
            else:
                plot += facet_wrap(facet_names[0])
        if type_x.is_timestamp():
            plot += scale_x_datetime()
        if self.y is not None and type_y.is_timestamp():
            plot += scale_y_datetime()
        if self.coord_flip:
            plot += coord_flip()

        if PyProjectSettings()._get_setting("dark-mode") is True:
            plot += flavor_darcula()

        return plot
