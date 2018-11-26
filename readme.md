# modanet-eval

Initial data evaluation of [ModaNet](https://github.com/eBay/modanet) by [eBay](https://github.com/eBay).

## Usage

Check the [dependencies](#dependencies), clone this repository and setup a new [conda](https://conda.io/miniconda.html) environment:

```bash
$ git clone https://github.com/nok/modanet-eval.git && cd modanet-eval 
$ conda env create -n modanet-eval -f environment.yml && source modanet-eval
```

Start all downloads with a passed destination path:

```bash
$ bash start_download.sh ~/Downloads/modanet
```

(Optional) Count the missing values and create a report:

```bash
$ python start_evaluation.py ~/Downloads/modanet
```

## Dependencies

- macOS: `brew install aria2 wget`
- Debian: `sudo apt-get install aria2 gzip wget`


## License

The developed software is Open Source Software released under the [MIT](license.txt) license. But pay attention to the licences of the related repositories, in particular [ModaNet](https://github.com/eBay/modanet/blob/master/LICENSE) and [paperdoll](https://github.com/kyamagu/paperdoll/blob/master/LICENSE.txt).   
