import os

NASA_TITLE_URL = {
    "global": "https://trek.nasa.gov/tiles/Mars/EQ/Mars_Viking_MDIM21_ClrMosaic_global_232m/1.0.0/default/default028mm/{z}/{y}/{x}.jpg", 
    "moon": "https://trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/1.0.0//default/default028mm/{z}/{y}/{x}.jpg",
    "mercury": "https://trek.nasa.gov/tiles/Mercury/EQ/Mercury_MESSENGER_MDIS_Basemap_BDR_Mosaic_Global_166m/1.0.0//default/default028mm/{z}/{y}/{x}.jpg"
}

def get_local_tile_path(dataset: str, z: int, x: int, y: int) -> str:
    return os.path.join("tiles", dataset, "latest", str(z), str(y), f"{x}.jpg")

def get_nasa_tile_url(z: int, x: int, y: int, dataset: str = "global") -> str:
    url_template = NASA_TITLE_URL.get(dataset)
    if not url_template:
        raise ValueError(f"DATASET {dataset} is not supported")
    
    return url_template.format(z=z, x=x, y=y)
