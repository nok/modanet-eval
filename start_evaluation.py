# -*- coding: utf-8 -*-

import sys
from datetime import datetime
from pathlib import Path
import json
import sqlite3
import pandas as pd


def main():

    # Download directory:
    down_dir = Path('.') / 'data'
    args = sys.argv[1:]
    if len(args) > 0 and Path(args[0]).is_dir():
        down_dir = Path(args[0])

    # Paperdoll (Chicktopia)
    paperdoll_db_path = down_dir / 'chictopia.sqlite3'
    if not paperdoll_db_path.exists():
        err = 'No database found'
        raise FileExistsError(err)

    conn_str = 'file:' + str(paperdoll_db_path) + '?mode=ro'
    paperdoll_db_conn = sqlite3.connect(conn_str, uri=True)
    paperdoll_db_sql = """
        SELECT
            id AS photo_id,
            path
        FROM
            photos
        WHERE
            photos.post_id IS NOT NULL
        AND
            photos.file_file_size IS NOT NULL
    """
    df_paperdoll = pd.read_sql(paperdoll_db_sql, con=paperdoll_db_conn).astype({
        'photo_id': 'int64',
    })

    # Downloaded files:
    file_names = down_dir.glob('images/**/*.jpg')
    file_names = [str(f.name) for f in file_names]

    # Modanet
    for modanet_json_path in down_dir.glob('modanet2018_*.json'):

        # Load data:
        with open(str(modanet_json_path), 'r', encoding='utf-8') as f:
            modanet_json_data = json.load(f)

        df_modanet = pd.DataFrame.from_dict(modanet_json_data['images']).astype(dtype={
            'id': 'int64',
            'file_name': 'str',
        }).rename({
            'id': 'photo_id'
        }, axis='columns')

        df = df_modanet.merge(df_paperdoll, on='photo_id', how='inner')

        df = df.replace([None], '')
        df.set_index(['photo_id'], inplace=True)
        df.sort_index(inplace=True)
        df = df[['file_name']]

        df['file_available'] = df['file_name'].apply(lambda x: x in file_names)
        df_missing = df[df['file_available'] == False]
        num_overall = len(df)
        num_missing = len(df_missing)

        ts = datetime.now()
        res = {
            'meta': {
                'file_name': modanet_json_path.name,
                'datetime': ts.strftime('%Y-%m-%dT%H:%M:%S'),
                'description': {
                    'ids': 'List of image ids which are inaccessible.'
                }
            },
            'stats': {
                'num_overall': num_overall,
                'num_missing': num_missing,
                'per_missing': '{:.4f}'.format(num_missing / num_overall)
            },
            'data': {
                'ids': df_missing.index.tolist()
            }
        }
        file_path = str(modanet_json_path) + '.{}.json'.format(
            ts.strftime('%Y_%m_%d_%H_%M_%S'))
        with open(file_path, 'w') as fp:
            json.dump(res, fp)


if __name__ == "__main__":
    main()
