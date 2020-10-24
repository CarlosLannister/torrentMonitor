#!/usr/bin/env python3

from elasticsearch import Elasticsearch
from countryinfo import CountryInfo
import libtorrent as lt
import geoip2.database
from datetime import date, datetime
import argparse
import time
import csv 
import sys
import os 

class torrentTracker:
    def __init__(self, torrent, output, elastic, geo, time):
        self.torrent = torrent
        self.output = output
        self.elastic = elastic
        self.geo = geo
        self.time = time 
        settings = {
            'user_agent': '',
            'listen_interfaces': '0.0.0.0:6881',
            'download_rate_limit': 10000,
            'upload_rate_limit': 0,
            'connections_limit': 800,
            'alert_mask': lt.alert.category_t.all_categories,
            'outgoing_interfaces': '',
            'announce_to_all_tiers': True,
            'announce_to_all_trackers': True,
            'auto_manage_interval': 5,
            'auto_scrape_interval': 0,
            'auto_scrape_min_interval': 0,
            'max_failcount': 1,
            'aio_threads': 8,
            'checking_mem_usage': 2048,
        }
        self.ses = lt.session(settings)

    def save_elasticsearch_es(self, index, data):
        es = Elasticsearch(hosts="localhost:9200")

        es.indices.create(
            index=index,
            ignore=400  # ignore 400 already exists code
        )
        id_case = str(datetime.strptime(data['date'], "%Y-%m-%d")) + \
            '-'+data['ip']
        es.update(index=index, id=id_case, body={'doc':data,'doc_as_upsert':True})


    def addTorrent(self):
        print(self.torrent)
        if self.torrent.startswith('magnet:'):
            atp = lt.add_torrent_params()
            atp = lt.parse_magnet_uri(self.torrent)
            atp.save_path = '.'
            h = self.ses.add_torrent(atp)
        else:
            info = lt.torrent_info(self.torrent)
            h = self.ses.add_torrent({'ti': info, 'save_path': '.'})

        return h 

    def main(self):
        h = torrentTracker.addTorrent(self)
        s = h.status()
        
        print('Starting tracking', s.name)

        if self.output:
            f = open(self.output + '.csv', 'a+')
            fieldnames = ['ip', 'client','version','countryISO', 'country', 'date']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

        if self.geo:
            reader = geoip2.database.Reader('./GeoLite2-Country.mmdb')
        try:
            while (1):
                s = h.status()

                print('\r%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % (
                    s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
                    s.num_peers, s.state), end=' ', flush=True)

                peers = h.get_peer_info()
                print("Saving %i peers" % len(peers))
                today = date.today()
                if peers:
                    for p in peers:
                        ip, port  = p.ip

                        country = ''
                        countryISO = ''
                        if self.geo:
                            try:
                                response = reader.country(ip)
                                country = response.country.name
                                countryISO = response.country.iso_code
                            except Exception as e:
                                print(e)
                        
                        client = ''
                        version = ''
                        try: 
                            client = p.client.decode("utf-8")
                            if client:
                                if '/' in client:
                                    metadata = client.split('/')
                                else:
                                    metadata = client.split(' ')
                                    
                                if len(metadata) > 1:
                                    client = metadata[0]
                                    version = metadata[1]
                                else:
                                    client = metadata
                        except Exception as e:
                            print(e)

                        peerDict = {'ip': ip, 'client': client, 'version': version, 
                            'countryISO': countryISO,'country': country, 'date': today.strftime("%Y-%m-%d")}
                        
                        if self.elastic:
                            self.save_elasticsearch_es('mulan', peerDict)

                        if self.output:
                            writer.writerow({'ip': ip,'client': client, 'version': version ,  
                            'countryISO': countryISO,'country': country, 'date': today.strftime("%Y-%m-%d %H:%M:%S")})
                        
                    time.sleep(int(self.time))
                sys.stdout.flush()
                time.sleep(.1)
        except KeyboardInterrupt:
            print("Cleaning up")
            if self.output:
                f.close()
            if self.geo:
                reader.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', "--torrent", help="Torrent file or magnet", required=True)
    parser.add_argument("-g", "--geo", help="Enable IP geolocation", default=False, action='store_true')  
    parser.add_argument("-o", "--output", help="Output path", default=False)     
    parser.add_argument("-ek", "--elastic", help="Enable elastic saving", default=False, action='store_true') 
    parser.add_argument("-T", "--time", help="Sleeping time between downloading peers", default=30)         
    args = parser.parse_args()

    if not (args.elastic or args.output):
        parser.error('You need to speficy a log output or enable elastic saving option')
    else:
        t = torrentTracker(args.torrent, args.output, args.elastic, args.geo, args.time)
        t.main()
