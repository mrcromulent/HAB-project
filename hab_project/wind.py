class Wind:

    def __init__(self, band_width=500.0):
        self.bands = []
        self.band_width = band_width

    def is_empty(self):
        return len(self.bands) == 0

    def add_band(self, alt, lat, lon, curr_time, d_lat_dt, d_lon_dt):

        self.bands.append(
            {
                "top_height": alt,
                "lat":        lat,
                "lon":        lon,
                "time":       curr_time,
                "d_lat_dt":   d_lat_dt,
                "d_lon_dt":   d_lon_dt
            }
        )

    def get_top_band_info(self):
        return self.bands[-1].values()

    def highest_band_height(self):
        if self.is_empty():
            raise ValueError
        else:
            return self.bands[-1]["top_height"]

    def return_lower_bands(self, alt):
        """Returns all bands partially or completely lower than alt.

        :param alt: Altitude in m
        :return:
        """
        top = 0
        for i, b in enumerate(self.bands):
            if b["top_height"] < alt:
                top = i
        return self.bands[:top+1]
