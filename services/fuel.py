import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

HOME_LAT = 42.99451255660583
HOME_LON = 12.67093749650644
MAX_DISTANCE = 10

PREZZI_URL = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
IMPIANTI_URL = "https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"

_geolocator = Nominatim(user_agent="discord-fuel-bot")


def _get_coordinates(position):
    if position is None:
        return HOME_LAT, HOME_LON

    if isinstance(position, str):
        position = position.replace(",", " ").strip()
        parts = position.split()

        # Coordinate
        if len(parts) == 2:
            try:
                return float(parts[0]), float(parts[1])
            except ValueError:
                pass

        # Città
        location = _geolocator.geocode(position)

        if location is None:
            raise ValueError("Città non trovata.")

        return location.latitude, location.longitude

    raise ValueError("Posizione non valida.")


def trova_distributori(position=None, max_distance=MAX_DISTANCE):

    lat, lon = _get_coordinates(position)

    prezzi = pd.read_csv(
        PREZZI_URL,
        sep="|",
        skiprows=1,
        encoding="utf-8"
    )

    impianti = pd.read_csv(
        IMPIANTI_URL,
        sep="|",
        skiprows=1,
        encoding="utf-8",
        engine="python",
        on_bad_lines="skip"
    )

    df = pd.merge(prezzi, impianti, on="idImpianto")

    def migliore_carburante(nome):

        carburante = df[df["descCarburante"] == nome].copy()

        carburante = carburante.dropna(
            subset=["Latitudine", "Longitudine"]
        )

        carburante["Latitudine"] = pd.to_numeric(
            carburante["Latitudine"],
            errors="coerce"
        )

        carburante["Longitudine"] = pd.to_numeric(
            carburante["Longitudine"],
            errors="coerce"
        )

        carburante = carburante.dropna(
            subset=["Latitudine", "Longitudine"]
        )

        carburante["Distanza"] = carburante.apply(
            lambda row: geodesic(
                (lat, lon),
                (row["Latitudine"], row["Longitudine"])
            ).km,
            axis=1
        )

        carburante = carburante[
            carburante["Distanza"] <= max_distance
        ]

        if carburante.empty:
            return None

        migliore = carburante.loc[
            carburante["prezzo"].idxmin()
        ]

        return {
            "Bandiera": migliore["Bandiera"],
            "Comune": migliore["Comune"],
            "Provincia": migliore["Provincia"],
            "Indirizzo": migliore["Indirizzo"],
            "Prezzo": float(migliore["prezzo"]),
            "Distanza": round(float(migliore["Distanza"]), 2),
            "Latitudine": float(migliore["Latitudine"]),
            "Longitudine": float(migliore["Longitudine"]),
            "Self": bool(migliore["isSelf"]),
            "DataAggiornamento": migliore["dtComu"]
        }

    return {
        "Benzina": migliore_carburante("Benzina"),
        "Gasolio": migliore_carburante("Gasolio")
    }