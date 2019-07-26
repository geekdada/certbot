import json
import os
import stat

import pkg_resources
import requests

PEBBLE_VERSION = 'v2.1.1-afe'
ASSETS_PATH = pkg_resources.resource_filename('certbot_integration_tests', 'assets')


def fetch(workspace):
    suffix = 'linux-amd64' if os.name != 'nt' else 'windows-amd64.exe'

    pebble_path = _fetch_asset('pebble', suffix)
    challtestsrv_path = _fetch_asset('pebble-challtestsrv', suffix)
    pebble_config_path = _build_pebble_config(workspace)

    return pebble_path, challtestsrv_path, pebble_config_path


def _fetch_asset(asset, suffix):
    asset_path = os.path.join(ASSETS_PATH, '{0}_{1}_{2}'.format(asset, PEBBLE_VERSION, suffix))
    if not os.path.exists(asset_path):
        asset_url = ('https://github.com/adferrand/pebble/releases/download/{0}/{1}_{2}'
                     .format(PEBBLE_VERSION, asset, suffix))
        response = requests.get(asset_url)
        response.raise_for_status()
        with open(asset_path, 'wb') as file_h:
            file_h.write(response.content)
    os.chmod(asset_path, os.stat(asset_path).st_mode | stat.S_IEXEC)

    return asset_path


def _build_pebble_config(workspace):
    config_path = os.path.join(workspace, 'pebble-config.json')
    with open(config_path, 'w') as file_h:
        file_h.write(json.dumps({
            'pebble': {
                'listenAddress': '0.0.0.0:14000',
                'certificate': os.path.join(ASSETS_PATH, 'cert.pem'),
                'privateKey': os.path.join(ASSETS_PATH, 'key.pem'),
                'httpPort': 5002,
                'tlsPort': 5001,
            },
        }))

    return config_path