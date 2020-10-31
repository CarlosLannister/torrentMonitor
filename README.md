# torrentMonitor
Track torrent downloads and save them!!! 

## Installation 

torrentMonitor uses libtorrent so first of all you will need to install it.

### Linux
```
sudo apt install python3-libtorrent
```

### Mac OS

```
brew install libtorrent-rasterbar
```

### Python dependencies
After install libtorrent with their python binding we will need to install the required dependecies with pip or pipenv. 

```
pip install -r requirements.txt 
```

```
pipenv install
pipevn shell
```

## Usage 

```
usage: torrentMonitor.py [-h] -t TORRENT [-g] [-o OUTPUT] [-ek] [-T TIME]

optional arguments:
  -h, --help            show this help message and exit
  -t TORRENT, --torrent TORRENT
                        Torrent file or magnet
  -g, --geo             Enable IP geolocation
  -o OUTPUT, --output OUTPUT
                        Output path
  -ek, --elastic        Enable elastic saving
  -T TIME, --time TIME  Sleeping time between downloading peers
```

Download a torrent file or copy a magnet link and specify it with -t option. 

```
python3 torrentMonitor.py -t AB4DEB4C2B2BE9EBCEB74955B3727BA45060C34B.torrent -o peers
```

## IP Geolocation 

You can geolocate the IPs using -g option of torrentMonitor. In order to use IP geolocation you will need Geolite Country database from maxmind. 

1. [Sign up for a MaxMind account](https://www.maxmind.com/en/geolite2/signup)
2. Set your password and create a [license key](https://www.maxmind.com/en/accounts/current/license-key)
3. Setup your download mechanism by using our [GeoIP Update program](https://dev.maxmind.com/geoip/geoipupdate/#For_Free_GeoLite2_Databases) or creating a [direct download script](https://dev.maxmind.com/geoip/geoipupdate/#Direct_Downloads)

```
python3 torrentMonitor.py -t AB4DEB4C2B2BE9EBCEB74955B3727BA45060C34B.torrent -o peers -g
```

## Save data into elastic 
Torrent monitor has the possibility of saving the ouput data into elastic with -ek option. You will need to have an elastic cluster running and specify the auth settings inside torrentMonitor. 

Just modify the following line with your own hosts data. 

```
es = Elasticsearch(hosts="localhost:9200")
```

