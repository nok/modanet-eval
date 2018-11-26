# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import sqlite3
import json
import pandas as pd


def main():

    # Download directory:
    down_dir = Path('.') / 'data'
    args = sys.argv[1:]
    if len(args) > 0 and Path(args[0]).is_dir():
        down_dir = Path(args[0])

    # Paperdoll (Chicktopia)
    paperdoll_db_path = down_dir / 'chictopia.sqlite3'
    conn_str = 'file:' + str(paperdoll_db_path) + '?mode=ro'
    paperdoll_db_conn = sqlite3.connect(conn_str, uri=True)
    paperdoll_db_sql = """
        SELECT
            id,
            path
        FROM
            photos
        WHERE
            photos.post_id IS NOT NULL
        AND
            photos.file_file_size IS NOT NULL
    """
    df_paperdoll = pd.read_sql(paperdoll_db_sql, con=paperdoll_db_conn).astype({
        'id': 'int64',
        'path': 'str',
    })

    # Modanet
    for modanet_json_path in down_dir.glob('modanet2018_*.json'):

        with open(str(modanet_json_path), 'r', encoding='utf-8') as f:
            modanet_json_data = json.load(f)

        df_modanet = pd.DataFrame.from_dict(modanet_json_data['images']).astype(dtype={
            'id': 'int64',
            'file_name': 'str',
        })

        df = df_modanet.merge(df_paperdoll, on='id', how='inner')

        with open(str(modanet_json_path) + '.txt', 'wt') as f:
            for idx, row in df.iterrows():
                file_name, path = row.get('file_name'), row.get('path')
                uris = ['http://images{}.chictopia.com{}'.format(idx, path) for idx, _ in enumerate(range(4))]
                line = '\t'.join(uris) + '\n\t' + 'out={}\n'.format(file_name)
                f.write(line)


if __name__ == "__main__":
    main()
