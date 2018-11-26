#!/usr/bin/env bash

# File directory:
file_dir="$( cd "$(dirname "$0")" ; pwd -P )"

# Download directory:
down_dir="$file_dir/data"
if [[ $# -eq 1 ]] && [[ -d "$1" ]]; then
    down_dir=${@%/}
fi

# Start raw downloads:
echo "Start initial downloads ... please wait."
declare -a uris=(
    "https://github.com/eBay/modanet/raw/master/annotations/modanet2018_instances_val.json"
    "https://github.com/eBay/modanet/raw/master/annotations/modanet2018_instances_train.json"
    "https://github.com/kyamagu/paperdoll/raw/master/data/chictopia/chictopia.sql.gz"
)
for uri in "${uris[@]}"
do
    echo "Download: $uri"
    wget --content-disposition --timestamping -L -P "$down_dir" "$uri"
done

# Compare checksums:
if [[ $(type -p "md5") ]]; then
    echo "Compare checksums ... please wait."
    for file in $(find "$down_dir" -type f \( -iname \*.json -o -iname \*.gz \) -a ! -iname ".*")
    do
        if [[ $(md5 -q "$file") != $(< "$file_dir/data/$(basename "$file").md5") ]]; then
            echo "✕ (wrong checksum): $file"
        else
            echo "✓ (right checksum): $file"
        fi
    done
fi

# Setup SQLite database:
if [[ -f "$down_dir/chictopia.sql.gz" ]]; then
    echo "Setup database chictopia.sqlite3 ... please wait."
    gunzip -c "$down_dir/chictopia.sql.gz" | sqlite3 "$down_dir/chictopia.sqlite3"
fi

# Generate download links:
if [[ -f "$down_dir/chictopia.sqlite3" ]]; then
    echo "Setup download links ... please wait."
    python make_aria2_links.py "$down_dir"
fi

# Download validation images:
if [[ -f "$down_dir/modanet2018_instances_val.json.txt" ]]; then
    echo "Download validation images ... please wait."
    rm -rf "$down_dir/images/val"
    mkdir -p "$down_dir/images/val"
    aria2c \
        --allow-overwrite=true \
        --download-result=full \
        --console-log-level=warn \
        --max-concurrent-downloads=8 \
        --input-file="$down_dir/modanet2018_instances_val.json.txt" \
        --dir="$down_dir/images/val"
fi

# Download training images:
if [[ -f "$down_dir/modanet2018_instances_train.json.txt" ]]; then
    echo "Download training images ... please wait."
    rm -rf "$down_dir/images/train"
    mkdir -p "$down_dir/images/train"
    aria2c \
        --allow-overwrite=true \
        --download-result=full \
        --console-log-level=warn \
        --max-concurrent-downloads=8 \
        --input-file="$down_dir/modanet2018_instances_train.json.txt" \
        --dir="$down_dir/images/train"
fi

echo "Download finished."
