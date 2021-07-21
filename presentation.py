"""
CSC110 Course Project: Air Pollution and Forestry
=============================================================================
presentation.py
This contains functions for loading and presenting data. These functions will
be called by the bokeh Server.
=============================================================================
@athor: Tu Anh Pham
"""

import numpy
from typing import Optional
from bokeh.plotting import figure, Figure
from bokeh.io import doc
from bokeh.models import (Button, CategoricalColorMapper, ColumnDataSource, Title,
                          HoverTool, Label, Slider, Dropdown, Paragraph, Column,
                          RangeSlider)

from bokeh.layouts import row, column
from bokeh.palettes import Category20, Category10
from data_manager import DataManager
from regression import*


def load_data(manager: DataManager) -> None:
    """Returns a tuple of data necessary to create the gapmider plot."""
    manager.load_data('Data/gdp_per_capita_formatted.csv', 'gdp per capita')
    manager.load_data('Data/population_formatted.csv', 'population')
    manager.load_data('Data/hdi_formatted.csv', 'hdi')
    manager.load_data('Data/forest_area_formatted.csv', 'forest area (% of land area)')
    manager.load_data('Data/motor_vehicle_formatted.csv', 'motor vehicle per capita')
    manager.load_data('Data/manufacturing_formatted.csv', 'manufacturing (% of gdp)')
    manager.load_data('Data/industry_formatted.csv', 'industry (% of gdp)')
    manager.load_data('Data/coal_per_capita_formatted.csv', 'coal consumption per capita')
    manager.load_data('Data/oil_per_capita_formatted.csv', 'oil consumption per capita')
    manager.load_data('Data/gas_per_capita_formatted.csv', 'gas consumption per capita')
    manager.load_data('Data/fossil_fuel_formatted.csv', 'fossil fuel consumption (total)')


def bk_app(bk_document: doc) -> None:
    """This is a bokeh application.

    The function will be called every time a client establish a connection with the bokeh
    server. It initializes a layout and feeds callables to the bokeh document, which was created
    by the server and will be used by the server for the given session.
    """
    manager = DataManager('Data/air_pollution_formatted.csv')
    load_data(manager)

    first_section = setup_gapminder(bk_document, manager)
    second_section = setup_data_explorer(manager)
    layout = column(first_section, second_section)

    bk_document.add_root(layout)
    bk_document.title = "Presentation"


def setup_gapminder(bk_document: doc, manager: DataManager) -> Column:
    """Setting up for the "gapminder" part of the presentation by
    mutating the given bokeh document.

    Preconditions:
        - manager is already loaded with population, gdp, and air pollution data.
    """
    years = [1990, 1995, 2000, 2005] + [year for year in range(2010, 2018)]
    # Get data of the whole world. (When the default value of 'regions' is None)
    data = manager.get_gapminder_data_from_regions(years, 'population', 'gdp per capita',
                                                   'air pollution', region_type='region')
    regions = list(set(data[years[0]]['region']))

    source = ColumnDataSource(data=data[years[0]])
    plot = create_air_gpd_plot(source, regions)

    label = Label(x=50000, y=76, text=str(years[0]), text_font_size='73px', text_color='#A9A9A9')
    plot.add_layout(label)

    # The id of the callback function that will be saved in bk_document.
    callback_id = None
    # Creating ui components and their associating callables.
    play_button = Button(label='► Play')

    def gapminder_update() -> None:
        """Function will be called periodically by the server when ► Play is clicked.
        Update the state of the gapminder plot."""
        global callback_id
        if slider.value < 2010:
            year = slider.value + 5
        else:
            year = slider.value + 1
        if year > years[-1]:
            year = years[0]
        if year == years[-1]:
            play_button.label = '► Play'
            bk_document.remove_periodic_callback(callback_id)
        slider.value = year

    def slider_update(attrname, old, new) -> None:
        """Function called when the state of the slider is changed."""
        year = slider.value
        label.text = str(year)
        source.data = data[year]

    slider = Slider(start=years[0], end=years[-1], value=years[0], step=1, title="Year")
    slider.on_change('value', slider_update)

    def animate() -> None:
        """Function called when the play/pause button is clicked."""
        global callback_id
        if play_button.label == '► Play':
            play_button.label = '❚❚ Pause'
            callback_id = bk_document.add_periodic_callback(gapminder_update, 800)
        else:
            play_button.label = '► Play'
            bk_document.remove_periodic_callback(callback_id)

    play_button.on_click(animate)
    gapminder_ui = column(play_button, slider, margin=(10, 0, 0, 0))
    gapminder = row(gapminder_ui, plot, margin=(40, 0, 0, 0))
    gapminder_desc = Paragraph(text="""GDP per capita and the measured concentration of PM 2.5 
    (micrograms of PM2.5 per cubic meter of different countries over the years. The size of the 
    circles is population.""")
    return column(gapminder_desc, gapminder, margin=(40, 0, 0, 40))


def setup_data_explorer(manager: DataManager) -> Column:
    """Setting up for the "data explorer" part of the presentation.
    Returns a Column object, which is a component of the layout.

    Preconditions:
        - manager is loaded with at least two kinds of data.
    """
    # Creating dropdowns to explore more data.
    indicators = manager.indicators()
    indicator_menu = sorted([(indicator.capitalize(), indicator.capitalize())
                             for indicator in indicators])

    ind_var_dropdown = Dropdown(label='Independent Variable', menu=indicator_menu)
    dep_var_dropdown = Dropdown(label='Dependent Variable', menu=indicator_menu)

    reg_func_menu = [('Linear regression', 'Linear regression'),
                     ('Least-square exponential', 'Least-square exponential'),
                     ('None', 'None')]
    reg_func_dropdown = Dropdown(label='Regression Function', menu=reg_func_menu)

    region_menu = ['All'] + [None] + [(region, region) for region in manager.get_regions()] + \
                  [None] + [(subreg, subreg) for subreg in manager.get_subregions()]
    region_dropdown = Dropdown(label='Select Region', menu=region_menu)

    year_range_slider = RangeSlider(start=1990, end=2019, value=(1990, 2019),
                                    step=1, title="Time interval")
    plot_button = Button(label='Plot Data')
    explorer_buttons = column(ind_var_dropdown, dep_var_dropdown, reg_func_dropdown,
                              region_dropdown, year_range_slider, plot_button,
                              margin=(24, 0, 0, 0))

    explorer_plot = create_scatter_plot([], 'HDI', 'Air Pollution')
    data_explorer = row(explorer_buttons, explorer_plot, margin=(40, 0, 0, 0))

    def ind_var_update(event):
        """Function called when the independent variable dropdown is changed.
        This will update the label of the dropdown to the text chosen."""
        ind_var_dropdown.label = event.item

    def dep_var_update(event):
        """Function called when the dependent variable dropdown is changed.
        This will update the label of the dropdown to the text chosen."""
        dep_var_dropdown.label = event.item

    def reg_func_update(event):
        """Function called when the regression function dropdown is changed.
        This will update the label of the dropdown to the text chosen."""
        reg_func_dropdown.label = event.item

    def region_update(event):
        """Function called when the "choose region" dropdown is changed.
        This will update the label of the dropdown to the text chosen."""
        region_dropdown.label = event.item

    def plot_on_click() -> None:
        """Function called when plot button is clicked. It will create and display a
        plot based on the state of the dropdowns."""
        if region_dropdown.label == 'All' or region_dropdown.label == 'Select Region':
            selected_region = None
        else:
            selected_region = region_dropdown.label
        years = list(range(year_range_slider.value[0], year_range_slider.value[1] + 1))
        selected_points = manager.get_data_points(years,
                                                  ind_var_dropdown.label.lower(),
                                                  dep_var_dropdown.label.lower(),
                                                  selected_region)

        if reg_func_dropdown.label == 'Linear regression':
            new_plot = create_linear_regression_plot(selected_points,
                                                     ind_var_dropdown.label,
                                                     dep_var_dropdown.label,
                                                     selected_region)
        elif reg_func_dropdown.label == 'Least-square exponential':
            new_plot = create_exponential_regression_plot(selected_points,
                                                          ind_var_dropdown.label,
                                                          dep_var_dropdown.label,
                                                          selected_region)
        else:
            new_plot = create_scatter_plot(selected_points, ind_var_dropdown.label,
                                           dep_var_dropdown.label)
        data_explorer.children[1] = new_plot

    ind_var_dropdown.on_click(ind_var_update)
    dep_var_dropdown.on_click(dep_var_update)
    reg_func_dropdown.on_click(reg_func_update)
    region_dropdown.on_click(region_update)
    plot_button.on_click(plot_on_click)

    explorer_desc = Paragraph(text="""To explore more data, choose the variable names and 
    regression function, then click "Plot Data". """)
    return column(explorer_desc, data_explorer, margin=(80, 0, 0, 40))


def replace_plot(old: Figure, new: Figure) -> None:
    """Replace attribures of the old figure with that of the new figure."""
    old.renderers = new.renderers
    old.xaxis.axis_label = new.xaxis.axis_label
    old.yaxis.axis_label = new.yaxis.axis_label
    old.title = new.title


def create_air_gpd_plot(source: ColumnDataSource, regions: List[str]) -> Figure:
    """Create the plot with colored circles, which illustrates country GPD and air pollution
    in different regions of the world."""
    plot = figure(title='GDP per Capita and Air Pollution of the World',
                  x_range=(-1000, 120000), y_range=(0, 110),
                  plot_height=800, plot_width=800)

    plot.xaxis.axis_label = "GDP per person (US Dollars)"
    plot.yaxis.axis_label = "Air Pollution (concentration of PM 2.5)"

    if len(regions) < 4:
        my_palette = Category10[3]
    else:
        my_palette = Category20[len(regions)]

    color_mapper = CategoricalColorMapper(palette=my_palette, factors=regions)
    plot.circle(
        x='gdp per capita',
        y='air pollution',
        radius_dimension='y',
        size='population',
        source=source,
        fill_color={'field': 'region', 'transform': color_mapper},
        fill_alpha=0.8,
        line_color='#7c7e71',
        line_width=0.5,
        line_alpha=0.5,
        legend_group='region',
    )
    plot.add_tools(HoverTool(tooltips="@name", show_arrow=False, point_policy='follow_mouse'))

    return plot


def create_scatter_plot(points: List[Tuple[float, float]],
                        x_axis_name: str,
                        y_axis_name: str,
                        description: Optional[str] = None) -> Figure:
    """Returns a bokeh scatter plot with a regression line.

    Preconditions:
        - x_axis_name != ''
        - y_axis_name != ''
    """
    if points == []:
        description = 'No data to show.'

    x_coords, y_coords = convert_points(points)

    source = ColumnDataSource({'x': x_coords, 'y': y_coords})

    # Rendering the figure
    p = figure(title=description, x_axis_label=x_axis_name, y_axis_label=y_axis_name,
               plot_width=800, plot_height=800)

    # add a circle renderer with a size, color, and alpha
    p.scatter(x='x', y='y', line_color=None, size=5, fill_alpha=0.5, source=source)

    return p


def create_linear_regression_plot(points: List[Tuple[float, float]],
                                  x_axis_name: str,
                                  y_axis_name: str,
                                  description: Optional[str] = None) -> Figure:
    """Returns a bokeh scatter plot with a regression line.

    Preconditions:
        - x_axis_name != ''
        - y_axis_name != ''
    """
    # Rendering the figure
    p = create_scatter_plot(points, x_axis_name, y_axis_name, description)

    if points == []:
        return p    # Returning an empty scatter plot

    x_coords, y_coords = convert_points(points)
    a, b = linear_regression(points)
    r2 = calculate_r_squared(points, a, b)

    x_min = min(x_coords)
    x_max = max(x_coords)

    p.line([x_min, x_max],
           [evaluate_line(a, b, 0, x_min), evaluate_line(a, b, 0, x_max)],
           line_width=3,
           line_alpha=0.6,
           color='firebrick')

    p.title = Title(text=f"y = {round(a, 3)}x + ({round(b, 3)}), r^2 = {round(r2, 4)}")

    return p


def create_exponential_regression_plot(points: List[Tuple[float, float]],
                                       x_axis_name: str,
                                       y_axis_name: str,
                                       description: Optional[str] = None) -> Figure:
    """Returns a bokeh scatter plot with an exponential regression curve of best fit (least-
    square fit).

    Preconditions:
        - x_axis_name != ''
        - y_axis_name != ''
    """
    #  Initiate a scatter plot.
    p = create_scatter_plot(points, x_axis_name, y_axis_name, description)

    if points == []:
        return p    # Returning an empty scatter plot

    x_coords, y_coords = convert_points(points)
    a, b = least_square_exponential_regression(points)

    x_min = min(x_coords)
    x_max = max(x_coords)
    # Generate x-coordinates for the curve based on x-max and x-min.
    xx = numpy.linspace(x_min, x_max, 200)
    curve_x = xx.tolist()
    curve_y = [evaluate_exponential_curve(a, b, 0, x) for x in xx]

    p.line(curve_x, curve_y, line_width=3, line_alpha=0.6, color='firebrick')

    p.title = Title(text=f"y = {round(a, 4)} * (e**({round(b, 4)} * x))")
    return p


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={'max-line-length': 100})
