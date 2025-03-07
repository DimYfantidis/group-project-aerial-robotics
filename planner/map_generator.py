import folium
from branca.element import Template, MacroElement

class MapGenerator:
    def __init__(self, center, zoom_start=16):
        self.map = folium.Map(location=center, zoom_start=zoom_start)

    def add_polygon(self, locations, color, tooltip, weight=2, fill=True, fill_opacity=0.4):
        folium.Polygon(
            locations=locations,
            color=color,
            weight=weight,
            fill=fill,
            fill_opacity=fill_opacity,
            tooltip=tooltip
        ).add_to(self.map)

    def add_marker(self, location, popup, icon_color, icon="info-sign"):
        folium.Marker(
            location=location,
            popup=popup,
            icon=folium.Icon(color=icon_color, icon=icon)
        ).add_to(self.map)

    def add_polyline(self, locations, color, tooltip, weight=3, opacity=1.0):
        folium.PolyLine(
            locations=locations,
            color=color,
            weight=weight,
            opacity=opacity,
            tooltip=tooltip
        ).add_to(self.map)

    def add_legend(self, legend_html):
        legend = MacroElement()
        legend._template = Template(legend_html)
        self.map.get_root().add_child(legend)

    def fit_bounds(self):
        self.map.fit_bounds(self.map.get_bounds())

    def save(self, file_name):
        self.map.save(file_name)
