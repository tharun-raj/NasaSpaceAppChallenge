import os

NASA_TITLE_URL = {
    "viking": "http://s3-eu-west-1.amazonaws.com/whereonmars.cartodb.net/celestia_mars-shaded-16k_global/{z}/{x}/{y}.png",
}

def get_local_tile_path(dataset: str, z: int, x: int, y: int) -> str:
    return os.path.join("tiles", dataset, "latest", str(z), str(y), f"{x}.jpg")

def get_nasa_tile_url(dataset: str, z: int, x: int, y: int) -> str:
    url_template = NASA_TITLE_URL.get(dataset)
    if not url_template:
        raise ValueError(f"DATASET {dataset} is not supported")
    
    return url_template.format(z=z, x=x, y=y)